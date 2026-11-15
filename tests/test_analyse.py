"""Tests for pipeline/analyse.py (issue #17). Seeded, no network, no real files."""
import json
from pathlib import Path

import jsonschema
import numpy as np
import pandas as pd

from pipeline import analyse

SCHEMAS = Path(__file__).resolve().parent.parent / "docs" / "contract"
YEARS = np.arange(2001, 2026)


def fake_box(box: str, dataset: str = "IMERG V07", slope: float = 0, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "dataset": dataset,
        "box": box,
        "year": YEARS,
        "total_mm": 3700 + slope * (YEARS - YEARS[0]) + rng.normal(0, 300, YEARS.size),
        "months_present": 12,
        "complete": "true",
    })


def fake_cells(n_side: int = 3) -> pd.DataFrame:
    frames = []
    for i in range(n_side):
        for j in range(n_side):
            df = fake_box("cell", seed=10 * i + j)
            df["lat"] = round(3.95 + 0.1 * i, 2)
            df["lon"] = round(9.65 + 0.1 * j, 2)
            frames.append(df[["lat", "lon", "year", "total_mm", "complete"]])
    return pd.concat(frames, ignore_index=True)


def envelope(payload: dict) -> dict:
    return {"contract_version": "1.0", "generated_at": "2026-11-15T00:00:00Z", "is_mock": True, **payload}


def validate(name: str, payload: dict) -> None:
    schema = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(envelope(payload), schema)


def test_verdict_three_cases():
    assert analyse.verdict(0.01, 5.0) == "significant_increase"
    assert analyse.verdict(0.01, -5.0) == "significant_decrease"
    assert analyse.verdict(0.30, 5.0) == "no_significant_trend"
    assert analyse.verdict(0.30, -5.0) == "no_significant_trend"


def test_strong_trend_detected():
    h = analyse.build_headline(fake_box("box_3x3", slope=60))
    assert h["verdict"] == "significant_increase"
    assert h["sen_ci95"][0] <= h["sen_slope_mm_per_year"] <= h["sen_ci95"][1]


def test_pettitt_change_year_is_first_year_of_new_regime():
    df = fake_box("box_3x3")
    df.loc[df["year"] >= 2014, "total_mm"] += 2000
    assert analyse.build_headline(df)["pettitt"]["change_year"] == 2014


def test_primary_test_follows_autocorrelation():
    h = analyse.build_headline(fake_box("box_3x3", slope=60))
    expected = "hamed_rao" if h["autocorr_significant"] else "original"
    assert h["mk_test_used"] == expected


def test_incomplete_years_are_dropped(tmp_path):
    df = fake_box("box_3x3")
    df["complete"] = "true"
    df.loc[0, "complete"] = "False"
    path = tmp_path / "annual_box.csv"
    df.to_csv(path, index=False)
    loaded = analyse.load_complete(path)
    assert len(loaded) == len(df) - 1
    assert 2001 not in loaded["year"].tolist()


def test_gpcp_row_omitted_when_absent():
    df = pd.concat([fake_box("box_3x3"), fake_box("box_1x1", seed=1), fake_box("box_5x5", seed=2)])
    rows = analyse.build_sensitivity(df)
    assert [r["box"] for r in rows] == ["box_1x1", "box_5x5"]
    assert all(r["dataset"] != "GPCP V3.3" for r in rows)


def test_gpcp_row_present_when_given():
    df = pd.concat([fake_box("box_3x3"), fake_box("box_3x3", dataset="GPCP V3.3", seed=3)])
    rows = analyse.build_sensitivity(df)
    assert [(r["box"], r["dataset"]) for r in rows] == [("box_3x3", "GPCP V3.3")]


def test_spatial_unavailable_under_plan_b():
    s = analyse.build_spatial(None, plan_b=True)
    assert s["available"] is False
    assert s["cells"] == []
    validate("spatial", s)


def test_spatial_counts_and_false_positives():
    s = analyse.build_spatial(fake_cells(3), plan_b=False)
    assert s["n_cells"] == 9
    assert s["expected_false_positives"] == 0.45
    assert s["n_significant"] == sum(c["p"] < 0.05 for c in s["cells"])
    validate("spatial", s)


def test_analysis_matches_contract_schema():
    df = pd.concat([fake_box("box_3x3"), fake_box("box_1x1", seed=1), fake_box("box_5x5", seed=2)])
    payload = {"headline": analyse.build_headline(df), "sensitivity": analyse.build_sensitivity(df)}
    validate("analysis", payload)
    json.dumps(payload)  # no numpy types left