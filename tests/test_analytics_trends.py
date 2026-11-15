"""Tests for app/services/analytics/trends.py. Seeded, no network."""
import numpy as np
import pandas as pd

from app.schemas.analysis import Headline, SensitivityRow, SpatialCell
from app.services.analytics import trends
from app.services.gis.regions import get_region
from app.services.gis.spatial import RegionAnnual

YEARS = np.arange(2001, 2026)
DOUALA = get_region("douala")
MAROUA = get_region("maroua")


def fake_annual(slope: float = 0, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "year": YEARS,
        "total_mm": 3700 + slope * (YEARS - YEARS[0]) + rng.normal(0, 300, YEARS.size),
        "months_present": 12,
        "complete": True,
    })


def fake_cells(n_side: int = 3) -> pd.DataFrame:
    frames = []
    for i in range(n_side):
        for j in range(n_side):
            df = fake_annual(seed=10 * i + j)
            df["lat"] = round(3.95 + 0.1 * i, 2)
            df["lon"] = round(9.65 + 0.1 * j, 2)
            frames.append(df)
    return pd.concat(frames, ignore_index=True)


def region_annual(box3: pd.DataFrame, region=DOUALA, others: bool = True) -> RegionAnnual:
    boxes = {"box_3x3": box3}
    if others:
        boxes |= {"box_1x1": fake_annual(seed=1), "box_5x5": fake_annual(seed=2)}
    return RegionAnnual(region=region, kind="region", boxes=boxes, cells=None)


def test_verdict_three_cases():
    assert trends.verdict(0.01, 5.0) == "significant_increase"
    assert trends.verdict(0.01, -5.0) == "significant_decrease"
    assert trends.verdict(0.30, 5.0) == "no_significant_trend"
    assert trends.verdict(0.30, -5.0) == "no_significant_trend"


def test_strong_trend_detected():
    h = trends.build_headline(region_annual(fake_annual(slope=60)))
    assert h["verdict"] == "significant_increase"
    assert h["sen_ci95"][0] <= h["sen_slope_mm_per_year"] <= h["sen_ci95"][1]
    Headline(**h)  # matches the API schema


def test_pettitt_change_year_is_first_year_of_new_regime():
    df = fake_annual()
    df.loc[df["year"] >= 2014, "total_mm"] += 2000
    assert trends.build_headline(region_annual(df))["pettitt"]["change_year"] == 2014


def test_primary_test_follows_autocorrelation():
    h = trends.build_headline(region_annual(fake_annual(slope=60)))
    assert h["mk_test_used"] == ("hamed_rao" if h["autocorr_significant"] else "original")


def test_incomplete_years_are_dropped():
    df = fake_annual()
    df.loc[0, "complete"] = False
    h = trends.build_headline(region_annual(df))
    assert h["n_years"] == len(df) - 1 and h["period"] == "2002-2025"


def test_caveats_depend_on_region_and_period():
    assert trends.caveats_for(DOUALA, 2001, 2025) == ["sensor_change_2014", "coastal_skill", "short_record", "area_estimate"]
    assert trends.caveats_for(MAROUA, 2001, 2025) == ["sensor_change_2014", "short_record", "area_estimate"]
    assert trends.caveats_for(MAROUA, 2014, 2025) == ["short_record", "area_estimate"]


def test_sensitivity_rows_skip_missing_boxes():
    rows = trends.build_sensitivity(region_annual(fake_annual()))
    assert [r["box"] for r in rows] == ["box_1x1", "box_5x5"]
    [SensitivityRow(**r) for r in rows]
    assert trends.build_sensitivity(region_annual(fake_annual(), others=False)) == []


def test_spatial_unavailable_under_plan_b():
    s = trends.build_spatial(None)
    assert s["available"] is False and s["cells"] == []


def test_spatial_counts_and_false_positives():
    s = trends.build_spatial(fake_cells(3))
    assert s["n_cells"] == 9
    assert s["expected_false_positives"] == 0.45
    assert s["n_significant"] == sum(c["p"] < 0.05 for c in s["cells"])
    [SpatialCell(**c) for c in s["cells"]]
