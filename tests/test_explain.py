"""Tests for pipeline/explain.py. Owner: AI (issue #20). No network."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from pipeline import explain as ex

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
SCHEMA = json.loads((ROOT / "docs" / "contract" / "explanation.schema.json").read_text(encoding="utf-8"))

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


def test_template_passes_on_current_analysis_json():
    analysis = json.loads(ex.ANALYSIS_PATH.read_text(encoding="utf-8"))
    ex.assert_checks(ex.build_template(analysis), analysis)


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
def test_main_writes_valid_explanation(name, tmp_path, monkeypatch):
    analysis_path = tmp_path / "analysis.json"
    out_path = tmp_path / "explanation.json"
    analysis_path.write_text(json.dumps(load(name)), encoding="utf-8")
    monkeypatch.setattr(ex, "ANALYSIS_PATH", analysis_path)
    monkeypatch.setattr(ex, "EXPLANATION_PATH", out_path)
    assert ex.main([]) == 0
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert not list(Draft202012Validator(SCHEMA).iter_errors(written))
    assert written["source"] == "template"
    assert written["model"] is None
    assert written["checks_passed"] is True
    assert written["is_mock"] is True


def test_main_records_failure(tmp_path, monkeypatch, capsys):
    analysis = load("no_trend")
    analysis_path = tmp_path / "analysis.json"
    out_path = tmp_path / "explanation.json"
    analysis_path.write_text(json.dumps(analysis), encoding="utf-8")
    monkeypatch.setattr(ex, "ANALYSIS_PATH", analysis_path)
    monkeypatch.setattr(ex, "EXPLANATION_PATH", out_path)
    original = ex.build_template

    def broken(a):
        fields = original(a)
        fields["summary"] += " Rainfall is stable."
        return fields

    monkeypatch.setattr(ex, "build_template", broken)
    assert ex.main([]) == 1
    assert json.loads(out_path.read_text(encoding="utf-8"))["checks_passed"] is False
    assert "banned wording" in capsys.readouterr().err


def test_fixtures_are_not_mutated():
    analysis = load("increase")
    before = copy.deepcopy(analysis)
    ex.build_template(analysis)
    ex.run_checks(ex.build_template(analysis), analysis)
    assert analysis == before
