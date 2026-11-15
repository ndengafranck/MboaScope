"""Headline, sensitivity and trend map. CLI: python -m pipeline.analyse. Owner: Analytics (issue #17)."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from pipeline import stats
from pipeline.common import INTERIM, WEB_DATA, is_mock_run, read_sources, write_json

ALPHA = 0.05
HEADLINE_BOX = "box_3x3"
HEADLINE_DATASET = "IMERG V07"
CAVEATS = ["sensor_change_2014", "coastal_skill", "short_record", "area_estimate"]
SENSITIVITY_RUNS = [
    ("box_1x1", "IMERG V07"),
    ("box_5x5", "IMERG V07"),
    ("box_3x3", "GPCP V3.3"),
]


def load_complete(path: Path | str) -> pd.DataFrame:
    """Read an annual CSV and keep complete years only, in time order."""
    df = pd.read_csv(path)
    keep = df["complete"].astype(str).str.lower() == "true"
    return df[keep].sort_values("year").reset_index(drop=True)


def verdict(p: float, slope: float, alpha: float = ALPHA) -> str:
    """Contract verdict from the primary test p-value and the sign of Sen's slope."""
    if p < alpha and slope > 0:
        return "significant_increase"
    if p < alpha and slope < 0:
        return "significant_decrease"
    return "no_significant_trend"


def analyse_series(years: Sequence[int], totals: Sequence[float]) -> dict:
    """Run every test on one annual series. Numbers stay unrounded here."""
    years = np.asarray(years)
    totals = np.asarray(totals, dtype=float)
    r1, r1_sig = stats.lag1_autocorr(totals)
    orig = stats.mk_original(totals)
    hr = stats.mk_hamed_rao(totals)
    primary = hr if r1_sig else orig
    slope, intercept0, low, high = stats.sen_slope_ci(years, totals)
    first = int(years[0])
    idx, k, p_pet = stats.pettitt(totals)
    mean = float(np.mean(totals))
    return {
        "first_year": first,
        "last_year": int(years[-1]),
        "n": int(totals.size),
        "mean": mean,
        "r1": r1,
        "r1_sig": r1_sig,
        "test_used": "hamed_rao" if r1_sig else "original",
        "orig": orig,
        "hr": hr,
        "p": primary["p"],
        "slope": slope,
        "low": low,
        "high": high,
        "intercept_first": intercept0 + slope * first,
        "pct_decade": slope * 10 / mean * 100,
        "change_year": int(years[idx]),
        "k": k,
        "p_pet": p_pet,
        "verdict": verdict(primary["p"], slope),
    }


def _select(df: pd.DataFrame, box: str, dataset: str) -> pd.DataFrame:
    return df[(df["box"] == box) & (df["dataset"] == dataset)].sort_values("year")


def build_headline(df: pd.DataFrame) -> dict:
    """Pre-registered headline: box_3x3, IMERG V07, full period."""
    sub = _select(df, HEADLINE_BOX, HEADLINE_DATASET)
    a = analyse_series(sub["year"].to_numpy(), sub["total_mm"].to_numpy())
    return {
        "box": HEADLINE_BOX,
        "dataset": HEADLINE_DATASET,
        "period": f"{a['first_year']}-{a['last_year']}",
        "n_years": a["n"],
        "alpha": ALPHA,
        "mean_annual_mm": int(round(a["mean"])),
        "lag1_autocorr": round(a["r1"], 2),
        "autocorr_significant": bool(a["r1_sig"]),
        "mk_test_used": a["test_used"],
        "mk_original": {
            "tau": round(a["orig"]["tau"], 2),
            "z": round(a["orig"]["z"], 2),
            "p": round(a["orig"]["p"], 3),
            "trend": a["orig"]["trend"],
        },
        "mk_hamed_rao": {
            "z": round(a["hr"]["z"], 2),
            "p": round(a["hr"]["p"], 3),
            "trend": a["hr"]["trend"],
        },
        "sen_slope_mm_per_year": round(a["slope"], 1),
        "sen_intercept_mm": int(round(a["intercept_first"])),
        "sen_ci95": [round(a["low"], 1), round(a["high"], 1)],
        "pct_per_decade": round(a["pct_decade"], 1),
        "pettitt": {
            "change_year": a["change_year"],
            "k": int(a["k"]),
            "p": round(a["p_pet"], 3),
            "significant": bool(a["p_pet"] < ALPHA),
        },
        "verdict": a["verdict"],
        "caveats": list(CAVEATS),
    }


def build_sensitivity(df: pd.DataFrame) -> list[dict]:
    """Robustness rows. A missing box or dataset is omitted, never faked."""
    rows = []
    for box, dataset in SENSITIVITY_RUNS:
        sub = _select(df, box, dataset)
        if len(sub) < stats.MIN_N:
            continue
        a = analyse_series(sub["year"].to_numpy(), sub["total_mm"].to_numpy())
        rows.append({
            "box": box,
            "dataset": dataset,
            "n_years": a["n"],
            "p": round(a["p"], 3),
            "sen_slope_mm_per_year": round(a["slope"], 1),
            "sen_ci95": [round(a["low"], 1), round(a["high"], 1)],
            "verdict": a["verdict"],
        })
    return rows


def build_spatial(cells: pd.DataFrame | None, plan_b: bool) -> dict:
    """Exploratory per-cell trend map. Unavailable under plan B."""
    if plan_b or cells is None:
        return {
            "exploratory": True,
            "available": False,
            "n_cells": 0,
            "alpha": ALPHA,
            "expected_false_positives": 0,
            "n_significant": 0,
            "cells": [],
        }
    out = []
    for (lat, lon), g in cells.groupby(["lat", "lon"]):
        g = g.sort_values("year")
        totals = g["total_mm"].to_numpy(dtype=float)
        if totals.size < stats.MIN_N:
            continue
        slope, _, _, _ = stats.sen_slope_ci(g["year"].to_numpy(), totals)
        p = stats.mk_original(totals)["p"]
        out.append({
            "lat": round(float(lat), 2),
            "lon": round(float(lon), 2),
            "mean_annual_mm": int(round(float(np.mean(totals)))),
            "sen_slope_mm_per_year": round(slope, 1),
            "p": round(p, 3),
        })
    n = len(out)
    return {
        "exploratory": True,
        "available": True,
        "n_cells": n,
        "alpha": ALPHA,
        "expected_false_positives": round(ALPHA * n, 2),
        "n_significant": int(sum(c["p"] < ALPHA for c in out)),
        "cells": out,
    }


def main() -> None:
    plan_b = read_sources()["access_method"] == "giovanni_csv"
    mock = is_mock_run()
    box = load_complete(INTERIM / "annual_box.csv")
    cells_path = INTERIM / "annual_cell.csv"
    cells = load_complete(cells_path) if cells_path.exists() and not plan_b else None
    write_json(
        WEB_DATA / "analysis.json",
        {"headline": build_headline(box), "sensitivity": build_sensitivity(box)},
        mock,
    )
    write_json(WEB_DATA / "spatial.json", build_spatial(cells, plan_b), mock)


if __name__ == "__main__":
    main()