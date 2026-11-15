"""Template explanation with number, claim and direction checks.

CLI: python -m pipeline.explain (make explain). Owner: AI (issue #20).

The AI layer never computes or decides anything. It only words numbers that
analysis.json already contains, and every field is checked before it is saved:

- number check: every number in the text must come from analysis.json (in its
  display rounding) or from a short list of fixed constants;
- claim check: no banned wording from docs/SCIENCE.md (cause, proof, "stable",
  station, forecast and so on), in any field, negated or not;
- direction check: the wording cannot contradict the verdict.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

from pipeline.common import WEB_DATA, write_json

ANALYSIS_PATH = WEB_DATA / "analysis.json"
EXPLANATION_PATH = WEB_DATA / "explanation.json"

FIELDS = ("summary", "what_it_means", "what_it_does_not_mean", "limitations")
VERDICTS = ("significant_increase", "significant_decrease", "no_significant_trend")

# Fixed numbers the text may use besides the values in analysis.json:
# 2014 (satellite transition), 0.05 (alpha), 5, 95 (confidence level), 1, 3,
# 11, 33, 55 (box sizes in km), 25, 10 (per decade).
FIXED_NUMBERS = (2014, 0.05, 5, 95, 1, 3, 11, 33, 55, 25, 10)

BOX_SIZE_KM = {"box_1x1": 11, "box_3x3": 33, "box_5x5": 55}

PETTITT_2014_SENTENCE = (
    "The change coincides with the 2014 satellite transition (TRMM to GPM), "
    "so it may be an artifact of the data rather than a real shift."
)

# Banned column of docs/SCIENCE.md. Word starts only, so "improve" and
# "unstable" do not match. No exemption for negated sentences.
BANNED_PATTERNS = (
    r"\bclimate change",
    r"\bglobal warming",
    r"\bdeforest",
    r"\burbani[sz]",
    r"\bhuman",
    r"\bprove",
    r"\bdid not change",
    r"\bdidn't change",
    r"\bno change in rainfall",
    r"\bstable\b",
    r"\bmeasured in\b",
    r"\bstation",
    r"\bgauge",
    r"\bwill increase",
    r"\bwill decrease",
    r"\bforecast",
    r"\bpredict",
)

FORBIDDEN_DIRECTION_WORDS = {
    "significant_increase": ("decreas", "drier", "less rain"),
    "significant_decrease": ("increas", "wetter", "more rain"),
    "no_significant_trend": (),
}

REQUIRED_SUMMARY_PHRASE = {
    "significant_increase": "statistically significant increase",
    "significant_decrease": "statistically significant decrease",
    "no_significant_trend": "no statistically significant trend",
}

# A minus sign only counts when it is not glued to a word or number before it,
# so the period "2001-2025" reads as 2001 and 2025, never as -2025.
# Accepts the ASCII hyphen, the Unicode minus and the en dash as a sign.
NUMBER_RE = re.compile(
    r"(?:(?<![\w.])[-−–])?"
    r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
    r"|(?:(?<![\w.])[-−–])?\.\d+"
)


class CheckError(ValueError):
    """Raised when an explanation fails one of the checks."""

    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


# ---------------------------------------------------------------- helpers


def _fmt(x: float | int) -> str:
    """Print a number as stored in analysis.json (already display-rounded)."""
    if isinstance(x, float) and x.is_integer() and abs(x) >= 100:
        return str(int(x))
    return str(x)


def _period_years(headline: dict[str, Any]) -> tuple[int, int]:
    start, end = (int(part) for part in str(headline["period"]).split("-"))
    return start, end


def _primary_p(headline: dict[str, Any]) -> float:
    key = "mk_hamed_rao" if headline["mk_test_used"] == "hamed_rao" else "mk_original"
    return headline[key]["p"]


def _test_name(headline: dict[str, Any]) -> str:
    if headline["mk_test_used"] == "hamed_rao":
        return (
            "the modified Mann-Kendall test (Hamed-Rao), used because each "
            "year's total was correlated with the year before"
        )
    return "the Mann-Kendall test"


def _box_phrase(headline: dict[str, Any]) -> str:
    km = BOX_SIZE_KM.get(headline["box"])
    return f"a box of about {km} km around Douala" if km else "a box around Douala"


def all_text(explanation: dict[str, Any]) -> str:
    """Join the four checked fields into one string."""
    parts = [explanation["summary"], explanation["what_it_means"], explanation["what_it_does_not_mean"]]
    parts.extend(explanation["limitations"])
    return "\n".join(parts)


# ---------------------------------------------------------------- template


def _summary(h: dict[str, Any]) -> str:
    low, high = h["sen_ci95"]
    start, end = _period_years(h)
    verdict = h["verdict"]
    if verdict == "significant_increase":
        finding = "a statistically significant increase in annual rainfall"
    elif verdict == "significant_decrease":
        finding = "a statistically significant decrease in annual rainfall"
    else:
        finding = "no statistically significant trend in annual rainfall"
    return (
        f"For {start}-{end}, the satellite record averaged over {_box_phrase(h)} shows {finding}. "
        f"The estimated change is {_fmt(h['sen_slope_mm_per_year'])} mm per year "
        f"(95% CI {_fmt(low)} to {_fmt(high)})."
    )


def _what_it_means(h: dict[str, Any]) -> str:
    p = _fmt(_primary_p(h))
    alpha = _fmt(h["alpha"])
    n = h["n_years"]
    pct = h["pct_per_decade"]
    mean = _fmt(h["mean_annual_mm"])
    low, high = h["sen_ci95"]
    test = _test_name(h)
    verdict = h["verdict"]

    if verdict == "significant_increase":
        text = (
            f"We used {test} on {n} annual totals. It gave p = {p}, below the {alpha} threshold, "
            f"so the upward tendency is unlikely to be only year-to-year chance. "
            f"The size of the rise is about {_fmt(abs(pct))}% per decade, compared with "
            f"a mean annual total of {mean} mm."
        )
    elif verdict == "significant_decrease":
        text = (
            f"We used {test} on {n} annual totals. It gave p = {p}, below the {alpha} threshold, "
            f"so the downward tendency is unlikely to be only year-to-year chance. "
            f"The size of the fall is about {_fmt(abs(pct))}% per decade, compared with "
            f"a mean annual total of {mean} mm."
        )
    else:
        text = (
            f"We used {test} on {n} annual totals. It gave p = {p}, which is not below the "
            f"{alpha} threshold, so the record cannot separate a steady upward or downward "
            f"tendency from ordinary year-to-year ups and downs. "
            f"The best estimate is {_fmt(pct)}% per decade, compared with a mean annual total "
            f"of {mean} mm."
        )
        if low < 0 < high:
            text += (
                " The 95% interval runs from a negative to a positive value, so the real "
                "change could go either way."
            )

    pettitt = h["pettitt"]
    if pettitt["significant"]:
        year = pettitt["change_year"]
        if 2013 <= year <= 2015:
            text += (
                f" The Pettitt test also found a step change starting in {year}. "
                + PETTITT_2014_SENTENCE
            )
        else:
            text += (
                f" The Pettitt test also found a step change starting in {year}, so part of "
                "the difference may come from one shift rather than a gradual trend."
            )
    return text


def _what_it_does_not_mean(h: dict[str, Any]) -> str:
    start, end = _period_years(h)
    return (
        "This result says nothing about why rainfall behaves this way: the tests describe a "
        "pattern in the numbers, not its reason. "
        f"It says nothing about future years: it covers {start}-{end} only. "
        "A result that is not statistically significant is not evidence that rainfall stayed "
        "the same, because a short record can miss a real but small change. "
        f"The value is a satellite estimate averaged over {_box_phrase(h)}, not a reading at "
        "one point in the city."
    )


def _limitation(code: str, h: dict[str, Any]) -> str:
    if code == "sensor_change_2014":
        return (
            "The satellites behind the data changed in 2014 (TRMM to GPM), and NASA warns "
            "that such a change can create artifacts that look like a trend in multi-year studies."
        )
    if code == "coastal_skill":
        return "NASA reports lower IMERG accuracy near coasts, and Douala sits on the Wouri estuary."
    if code == "short_record":
        return (
            f"With only {h['n_years']} annual values the tests have low statistical power, "
            "so a real but small change can go undetected."
        )
    if code == "area_estimate":
        return (
            f"The numbers are satellite estimates averaged over {_box_phrase(h)}, "
            "not readings at a single point."
        )
    raise ValueError(f"unknown caveat code: {code!r}")


def build_template(analysis: dict[str, Any]) -> dict[str, Any]:
    """The four explanation fields, built from analysis.json only."""
    h = analysis["headline"]
    if h["verdict"] not in VERDICTS:
        raise ValueError(f"unknown verdict: {h['verdict']!r}")
    return {
        "summary": _summary(h),
        "what_it_means": _what_it_means(h),
        "what_it_does_not_mean": _what_it_does_not_mean(h),
        "limitations": [_limitation(code, h) for code in h["caveats"]],
    }


# ---------------------------------------------------------------- checks


def _numbers_in(value: Any) -> Iterable[float]:
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float)):
        yield float(value)
    elif isinstance(value, dict):
        for v in value.values():
            yield from _numbers_in(v)
    elif isinstance(value, list):
        for v in value:
            yield from _numbers_in(v)


def _key(x: float) -> float:
    return round(float(x), 6)


def allowed_numbers(analysis: dict[str, Any]) -> set[float]:
    """Numbers the text may contain."""
    body = {k: v for k, v in analysis.items() if k not in ("contract_version", "generated_at", "is_mock")}
    allowed: set[float] = set()
    for x in _numbers_in(body):
        allowed.add(_key(x))
        allowed.add(_key(abs(x)))
    start, end = _period_years(analysis["headline"])
    allowed.update(_key(y) for y in range(start, end + 1))
    allowed.update(_key(x) for x in FIXED_NUMBERS)
    return allowed


def extract_numbers(text: str) -> list[tuple[str, float]]:
    """Every number written in the text, as (as written, value)."""
    found = []
    for match in NUMBER_RE.finditer(text):
        raw = match.group(0)
        cleaned = raw.replace(",", "").replace("−", "-").replace("–", "-")
        found.append((raw, float(cleaned)))
    return found


def check_numbers(text: str, analysis: dict[str, Any]) -> list[str]:
    allowed = allowed_numbers(analysis)
    return [f"number not in analysis.json: {raw}" for raw, value in extract_numbers(text) if _key(value) not in allowed]


def check_claims(text: str) -> list[str]:
    problems = []
    for pattern in BANNED_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            problems.append(f"banned wording: {match.group(0)!r}")
    return problems


def check_direction(explanation: dict[str, Any], verdict: str) -> list[str]:
    text = all_text(explanation).lower()
    problems = [
        f"direction word {word!r} contradicts verdict {verdict}"
        for word in FORBIDDEN_DIRECTION_WORDS[verdict]
        if word in text
    ]
    phrase = REQUIRED_SUMMARY_PHRASE[verdict]
    if phrase not in explanation["summary"].lower():
        problems.append(f"summary must contain {phrase!r}")
    return problems


def check_shape(explanation: dict[str, Any]) -> list[str]:
    problems = []
    for field in FIELDS[:3]:
        if not isinstance(explanation.get(field), str) or not explanation[field].strip():
            problems.append(f"{field} must be a non-empty string")
    lims = explanation.get("limitations")
    if not isinstance(lims, list) or len(lims) != 4 or not all(isinstance(s, str) and s.strip() for s in lims):
        problems.append("limitations must be a list of 4 non-empty strings")
    return problems


def run_checks(explanation: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
    """All problems found; an empty list means every check passed."""
    problems = check_shape(explanation)
    if problems:
        return problems
    text = all_text(explanation)
    problems += check_numbers(text, analysis)
    problems += check_claims(text)
    problems += check_direction(explanation, analysis["headline"]["verdict"])
    return problems


def assert_checks(explanation: dict[str, Any], analysis: dict[str, Any]) -> None:
    """Raise CheckError if any check fails (used in tests)."""
    problems = run_checks(explanation, analysis)
    if problems:
        raise CheckError(problems)


# ---------------------------------------------------------------- CLI


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def explain(analysis: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Template explanation plus the list of check problems (empty when clean)."""
    fields = build_template(analysis)
    problems = run_checks(fields, analysis)
    payload = {"source": "template", "model": None, "checks_passed": not problems, **fields}
    return payload, problems


def main(argv: list[str] | None = None) -> int:
    analysis = read_json(ANALYSIS_PATH)
    payload, problems = explain(analysis)
    write_json(EXPLANATION_PATH, payload, bool(analysis.get("is_mock", True)))
    if problems:
        # The template should never fail. If it does, the file is still written
        # with checks_passed false so the site can hide it, and the build stops.
        for problem in problems:
            print(f"explain: check failed: {problem}", file=sys.stderr)
        return 1
    print(f"explain: wrote {EXPLANATION_PATH} (source template, checks passed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
