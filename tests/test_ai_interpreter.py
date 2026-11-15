"""Tests for app/services/ai/interpreter.py. Owner: Developer B. No network."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from app.services.ai import interpreter as ex

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"

CASES = [
    "increase",
    "increase_pettitt2014",
    "decrease",
    "decrease_pettitt2014",
    "no_trend",
    "no_trend_pettitt2014",
]


def load(name: str) -> dict:
    return json.loads((FIXTURES / f"analysis_{name}.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------ template passes


@pytest.mark.parametrize("name", CASES)
def test_template_passes_all_checks(name):
    analysis = load(name)
    ex.assert_checks(ex.build_template(analysis), analysis)


def test_template_for_inland_region_has_three_limitations():
    analysis = load("increase")
    h = analysis["headline"]
    h["region_name"], h["region_id"] = "Maroua", "maroua"
    h["caveats"] = ["sensor_change_2014", "short_record", "area_estimate"]
    fields = ex.build_template(analysis)
    ex.assert_checks(fields, analysis)
    assert len(fields["limitations"]) == 3
    assert "around Maroua" in fields["summary"]
    assert "Douala" not in ex.all_text(fields)


def test_template_passes_with_hamed_rao():
    analysis = load("increase")
    analysis["headline"]["mk_test_used"] = "hamed_rao"
    analysis["headline"]["autocorr_significant"] = True
    fields = ex.build_template(analysis)
    ex.assert_checks(fields, analysis)
    assert "Hamed-Rao" in fields["what_it_means"]
    assert "p = 0.011" in fields["what_it_means"]


@pytest.mark.parametrize("name", ["increase_pettitt2014", "decrease_pettitt2014", "no_trend_pettitt2014"])
def test_pettitt_2014_sentence_added(name):
    fields = ex.build_template(load(name))
    assert ex.PETTITT_2014_SENTENCE in fields["what_it_means"]


@pytest.mark.parametrize("name", ["increase", "decrease", "no_trend"])
def test_no_pettitt_sentence_without_significant_change(name):
    fields = ex.build_template(load(name))
    assert ex.PETTITT_2014_SENTENCE not in fields["what_it_means"]
    assert "Pettitt" not in fields["what_it_means"]


def test_pettitt_other_year_gets_neutral_sentence():
    analysis = load("increase")
    analysis["headline"]["pettitt"] = {"change_year": 2008, "k": 120, "p": 0.02, "significant": True}
    fields = ex.build_template(analysis)
    ex.assert_checks(fields, analysis)
    assert ex.PETTITT_2014_SENTENCE not in fields["what_it_means"]
    assert "2008" in fields["what_it_means"]


@pytest.mark.parametrize("name", CASES)
def test_summary_carries_slope_ci_and_period(name):
    h = load(name)["headline"]
    summary = ex.build_template(load(name))["summary"]
    low, high = h["sen_ci95"]
    assert f"{h['sen_slope_mm_per_year']} mm per year" in summary
    assert f"95% CI {low} to {high}" in summary
    assert h["period"] in summary


@pytest.mark.parametrize("name", CASES)
def test_what_it_means_has_pct_and_test(name):
    h = load(name)["headline"]
    text = ex.build_template(load(name))["what_it_means"]
    assert f"{abs(h['pct_per_decade'])}% per decade" in text
    assert "Mann-Kendall" in text


@pytest.mark.parametrize("name", CASES)
def test_one_limitation_per_caveat(name):
    analysis = load(name)
    assert len(ex.build_template(analysis)["limitations"]) == len(analysis["headline"]["caveats"]) == 4


def test_unknown_caveat_raises():
    analysis = load("no_trend")
    analysis["headline"]["caveats"][0] = "made_up"
    with pytest.raises(ValueError):
        ex.build_template(analysis)


# ------------------------------------------------------------ number check


@pytest.mark.parametrize(
    "text, expected",
    [
        ("For 2001-2025", [2001.0, 2025.0]),
        ("(95% CI -4.1 to 37.9)", [95.0, -4.1, 37.9]),
        ("a total of 3,724 mm", [3724.0]),
        ("minus −4.1 here", [-4.1]),
        ("p = 0.168.", [0.168]),
        ("Mann-Kendall test, lag-1", [1.0]),
    ],
)
def test_extract_numbers(text, expected):
    assert [v for _, v in ex.extract_numbers(text)] == expected


@pytest.mark.parametrize("bad", ["14.5", "3725", "-14.4x", "0.169", "2026", "2000", "7"])
def test_injected_wrong_number_fails(bad):
    analysis = load("no_trend")
    fields = ex.build_template(analysis)
    fields["what_it_means"] += f" Extra value {bad.rstrip('x')} here."
    with pytest.raises(ex.CheckError, match="number not in analysis.json"):
        ex.assert_checks(fields, analysis)


def test_wrong_slope_in_summary_fails():
    analysis = load("increase")
    fields = ex.build_template(analysis)
    fields["summary"] = fields["summary"].replace("31.2", "32.1")
    with pytest.raises(ex.CheckError):
        ex.assert_checks(fields, analysis)


def test_negative_of_unsigned_value_fails():
    # Absolute values are allowed, but not a sign that is not in analysis.json.
    analysis = load("increase")
    fields = ex.build_template(analysis)
    fields["what_it_means"] += " That is -31.2 mm per year."
    with pytest.raises(ex.CheckError):
        ex.assert_checks(fields, analysis)


def test_thousands_separator_value_passes():
    analysis = load("no_trend")
    fields = ex.build_template(analysis)
    fields["what_it_means"] = fields["what_it_means"].replace("3724 mm", "3,724 mm")
    ex.assert_checks(fields, analysis)


# ------------------------------------------------------------ claim check

BANNED_PHRASES = [
    "This is caused by climate change.",
    "It confirms global warming.",
    "Deforestation explains it.",
    "Urbanisation explains it.",
    "Urbanization explains it.",
    "Human activity explains it.",
    "This proves a trend.",
    "Rainfall did not change.",
    "Rainfall didn't change.",
    "There was no change in rainfall.",
    "Rainfall is stable.",
    "Values were measured in Douala.",
    "This is not a station measurement.",
    "This is not rain gauge data.",
    "Rainfall will increase.",
    "Rainfall will decrease.",
    "This is not a forecast.",
    "We cannot predict next year.",
]


@pytest.mark.parametrize("phrase", BANNED_PHRASES)
@pytest.mark.parametrize("field", ["summary", "what_it_means", "what_it_does_not_mean", "limitations"])
def test_each_banned_phrase_fails_in_every_field(phrase, field):
    analysis = load("no_trend")
    fields = ex.build_template(analysis)
    if field == "limitations":
        fields["limitations"][2] += " " + phrase
    else:
        fields[field] += " " + phrase
    with pytest.raises(ex.CheckError, match="banned wording"):
        ex.assert_checks(fields, analysis)


@pytest.mark.parametrize("word", ["improve", "improved", "unstable", "approve"])
def test_word_start_matching_does_not_trip(word):
    analysis = load("no_trend")
    fields = ex.build_template(analysis)
    fields["what_it_means"] += f" More years would {word} this."
    ex.assert_checks(fields, analysis)


def test_banned_check_is_case_insensitive():
    assert ex.check_claims("CLIMATE CHANGE")
    assert ex.check_claims("Station")


# ------------------------------------------------------------ direction check


@pytest.mark.parametrize("word", ["decreasing", "drier", "less rain"])
def test_flipped_direction_fails_for_increase(word):
    analysis = load("increase")
    fields = ex.build_template(analysis)
    fields["what_it_means"] += f" The city became {word}."
    with pytest.raises(ex.CheckError, match="direction word"):
        ex.assert_checks(fields, analysis)


@pytest.mark.parametrize("word", ["increasing", "wetter", "more rain"])
def test_flipped_direction_fails_for_decrease(word):
    analysis = load("decrease")
    fields = ex.build_template(analysis)
    fields["limitations"][0] += f" The city became {word}."
    with pytest.raises(ex.CheckError, match="direction word"):
        ex.assert_checks(fields, analysis)


def test_summary_swapped_between_verdicts_fails():
    inc, dec = load("increase"), load("decrease")
    fields = ex.build_template(inc)
    fields["summary"] = ex.build_template(dec)["summary"]
    with pytest.raises(ex.CheckError):
        ex.assert_checks(fields, inc)


def test_no_trend_summary_needs_phrase():
    analysis = load("no_trend")
    fields = ex.build_template(analysis)
    fields["summary"] = fields["summary"].replace("no statistically significant trend", "no clear trend")
    with pytest.raises(ex.CheckError, match="no statistically significant trend"):
        ex.assert_checks(fields, analysis)


# ------------------------------------------------------------ shape and file


def test_bad_shape_fails():
    analysis = load("no_trend")
    fields = ex.build_template(analysis)
    fields["limitations"] = fields["limitations"][:3]
    with pytest.raises(ex.CheckError, match="limitations"):
        ex.assert_checks(fields, analysis)


@pytest.mark.parametrize("name", CASES)
def test_interpret_returns_checked_template(name):
    payload, notes = ex.interpret(load(name))
    assert notes == []
    assert payload["source"] == "template"
    assert payload["model"] is None
    assert payload["checks_passed"] is True


def test_interpret_reports_template_failure(monkeypatch):
    original = ex.build_template

    def broken(a):
        fields = original(a)
        fields["summary"] += " Rainfall is stable."
        return fields

    monkeypatch.setattr(ex, "build_template", broken)
    payload, notes = ex.interpret(load("no_trend"))
    assert payload["checks_passed"] is False
    assert any("banned wording" in n for n in notes)


def test_fixtures_are_not_mutated():
    analysis = load("increase")
    before = copy.deepcopy(analysis)
    ex.build_template(analysis)
    ex.run_checks(ex.build_template(analysis), analysis)
    assert analysis == before


# ------------------------------------------------------------ Gemini rewrite (#21), no network


def good_rewrite(template: dict) -> dict:
    """A plausible model answer: reworded, same numbers, same caveats."""
    return {
        "what_it_means": template["what_it_means"].replace("We used", "The team used"),
        "what_it_does_not_mean": template["what_it_does_not_mean"].replace("This result", "The result"),
        "limitations": [s.replace("The ", "These ", 1) if s.startswith("The numbers") else s for s in template["limitations"]],
    }


def fake_call(answer, model="gemini-test-flash"):
    def call(prompt: str):
        assert "{{" not in prompt, "prompt placeholders were not filled"
        return (answer if isinstance(answer, str) else json.dumps(answer)), model

    return call


@pytest.mark.parametrize("name", CASES)
def test_good_rewrite_is_kept(name):
    analysis = load(name)
    template = ex.build_template(analysis)
    payload, reasons = ex.rewrite_with_llm(analysis, template, fake_call(good_rewrite(template)))
    assert reasons == []
    assert payload["source"] == "gemini"
    assert payload["model"] == "gemini-test-flash"
    assert payload["checks_passed"] is True
    assert payload["summary"] == template["summary"]


def test_rewrite_with_code_fence_is_parsed():
    analysis = load("no_trend")
    template = ex.build_template(analysis)
    answer = "```json\n" + json.dumps(good_rewrite(template)) + "\n```"
    payload, reasons = ex.rewrite_with_llm(analysis, template, fake_call(answer))
    assert reasons == [] and payload["source"] == "gemini"


@pytest.mark.parametrize(
    "mutate, reason",
    [
        (lambda a: a.update(what_it_means=a["what_it_means"] + " That is 12.3 mm."), "number"),
        (lambda a: a.update(what_it_means=a["what_it_means"] + " Rainfall is stable."), "banned"),
        (lambda a: a.update(what_it_means=a["what_it_means"] + " It got drier."), "direction"),
        (lambda a: a.update(limitations=a["limitations"][:3]), "limitations"),
        (lambda a: a.update(limitations=[a["limitations"][1], a["limitations"][2], a["limitations"][3], "Coverage varies."]), "caveat"),
        (lambda a: a.update(what_it_does_not_mean="word " * 121), "words"),
        (lambda a: a.update(what_it_means=a["what_it_means"].replace("artifact", "oddity")), "artifact"),
        (lambda a: a.update(what_it_means=a["what_it_means"] + " Plain \u2014 text."), "em dash"),
    ],
)
def test_bad_rewrite_falls_back_to_template(mutate, reason):
    analysis = load("increase_pettitt2014")
    template = ex.build_template(analysis)
    answer = good_rewrite(template)
    mutate(answer)
    payload, reasons = ex.rewrite_with_llm(analysis, template, fake_call(answer))
    assert payload["source"] == "template"
    assert payload["model"] is None
    assert payload["what_it_means"] == template["what_it_means"]
    assert reasons
    assert reason in " ".join(reasons)


def test_rewrite_cannot_change_summary():
    analysis = load("no_trend")
    template = ex.build_template(analysis)
    answer = {**good_rewrite(template), "summary": "Something else entirely."}
    payload, _ = ex.rewrite_with_llm(analysis, template, fake_call(answer))
    assert payload["summary"] == template["summary"]


@pytest.mark.parametrize("answer", ["not json", "[1, 2]", ""])
def test_unparseable_answer_falls_back(answer):
    analysis = load("no_trend")
    template = ex.build_template(analysis)
    payload, reasons = ex.rewrite_with_llm(analysis, template, fake_call(answer))
    assert payload["source"] == "template" and "gemini error" in reasons[0]


def test_api_error_falls_back():
    def boom(prompt):
        raise RuntimeError("quota exceeded")

    analysis = load("no_trend")
    template = ex.build_template(analysis)
    payload, reasons = ex.rewrite_with_llm(analysis, template, boom)
    assert payload["source"] == "template"
    assert "quota exceeded" in reasons[0]


def test_prompt_contains_only_analysis_and_template():
    analysis = load("decrease")
    template = ex.build_template(analysis)
    prompt = ex.build_prompt(analysis, template)
    assert template["summary"] in prompt
    assert '"verdict": "significant_decrease"' in prompt
    assert "{{" not in prompt


@pytest.mark.parametrize(
    "names, expected",
    [
        (["models/gemini-2.0-flash", "models/gemini-2.5-flash", "models/gemini-2.5-pro"], "gemini-2.5-flash"),
        (["models/gemini-2.5-flash", "models/gemini-3.0-flash-preview", "models/gemini-3.0-flash"], "gemini-3.0-flash"),
        (["models/gemini-2.5-flash-lite", "models/gemini-2.5-flash-image", "models/gemini-2.0-flash"], "gemini-2.0-flash"),
        (["models/gemini-2.5-pro"], None),
    ],
)
def test_pick_flash_model(names, expected):
    assert ex.pick_flash_model(names) == expected


# ------------------------------------------------------------ interpret() with Gemini


def test_interpret_llm_without_key_returns_template(monkeypatch):
    monkeypatch.setattr(ex, "_gemini_settings", lambda: ("", ex.DEFAULT_MODEL))
    payload, notes = ex.interpret(load("no_trend"), use_llm=True)
    assert payload["source"] == "template"
    assert notes == ["GEMINI_API_KEY is not set"]


def test_interpret_llm_with_fake_model():
    analysis = load("no_trend")
    template = ex.build_template(analysis)
    payload, notes = ex.interpret(analysis, use_llm=True, call=fake_call(good_rewrite(template), "gemini-test-flash"))
    assert notes == []
    assert payload["source"] == "gemini" and payload["model"] == "gemini-test-flash"


def test_suggestions_split_at_2014():
    titles = [s["title"] for s in ex.suggest_investigations(load("no_trend_pettitt2014"))]
    assert "Repeat the test on the GPM era only" in titles
    assert "Repeat the test on the TRMM era only" in titles
    for s in ex.suggest_investigations(load("no_trend")):
        if s["region_id"]:
            assert s["end_year"] - s["start_year"] + 1 >= 10


def test_eval_without_llm_prints_table(capsys):
    assert ex.main(["--eval"]) == 0
    out = capsys.readouterr().out
    for case in CASES:
        assert f"| {case} | template |" in out


# ------------------------------------------------------------ retries on busy errors


class FakeApiError(Exception):
    def __init__(self, code):
        super().__init__(f"error {code}")
        self.code = code


def test_retry_succeeds_after_busy_errors():
    calls, waits = [], []

    def fn():
        calls.append(1)
        if len(calls) < 3:
            raise FakeApiError(503)
        return "ok"

    assert ex.with_retries(fn, waits=[1, 2, 3], sleep=waits.append) == "ok"
    assert waits == [1, 2]


def test_retry_gives_up_after_last_wait():
    def fn():
        raise FakeApiError(503)

    with pytest.raises(FakeApiError):
        ex.with_retries(fn, waits=[1, 2], sleep=lambda s: None)


@pytest.mark.parametrize("code", [400, 401, 403, 404, None])
def test_no_retry_on_other_errors(code):
    waits = []

    def fn():
        raise FakeApiError(code)

    with pytest.raises(FakeApiError):
        ex.with_retries(fn, waits=[1, 2], sleep=waits.append)
    assert waits == []
