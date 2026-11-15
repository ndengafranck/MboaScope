"""Headline trend, sensitivity rows and the exploratory trend map. Owner: Developer A (analytics tasks).

Pre-registered rules (docs/methodology.md): headline = box_3x3, IMERG V07,
alpha 0.05; Hamed-Rao is the primary test when lag-1 autocorrelation is
significant; Sen's slope and its 95% CI are always reported; other boxes are
robustness checks and are never promoted to the headline.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd

from app.core.config import ALPHA, DATASET, HEADLINE_BOX
from app.services.analytics import stats
from app.services.gis.regions import Region
from app.services.gis.spatial import RegionAnnual

SENSITIVITY_BOXES = ("box_1x1", "box_5x5")
SATELLITE_CHANGE_YEAR = 2014


def complete_only(annual: pd.DataFrame) -> pd.DataFrame:
    keep = annual["complete"].astype(str).str.lower() == "true"
    return annual[keep].sort_values("year").reset_index(drop=True)


def verdict(p: float, slope: float, alpha: float = ALPHA) -> str:
    if p < alpha and slope > 0:
        return "significant_increase"
    if p < alpha and slope < 0:
        return "significant_decrease"
    return "no_significant_trend"


def caveats_for(region: Region, first_year: int, last_year: int) -> list[str]:
    """Known threats that apply to this region and period, in display order."""
    out = []
    if first_year < SATELLITE_CHANGE_YEAR <= last_year:
        out.append("sensor_change_2014")
    if region.coastal:
        out.append("coastal_skill")
    out += ["short_record", "area_estimate"]
    return out


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


def headline_from(a: dict, region: Region, box: str = HEADLINE_BOX) -> dict:
    """Display-rounded headline (mm 0 dp, slopes 1 dp, p 3 dp, % 1 dp, r 2 dp)."""
    return {
        "region_id": region.id,
        "region_name": region.name,
        "box": box,
        "dataset": DATASET["label"],
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
        "caveats": caveats_for(region, a["first_year"], a["last_year"]),
    }


def build_headline(ra: RegionAnnual) -> dict:
    sub = complete_only(ra.boxes[HEADLINE_BOX])
    if len(sub) < stats.MIN_N:
        raise ValueError(f"only {len(sub)} complete years for {ra.region.id}; need at least {stats.MIN_N}")
    a = analyse_series(sub["year"].to_numpy(), sub["total_mm"].to_numpy())
    return headline_from(a, ra.region)


def build_sensitivity(ra: RegionAnnual) -> list[dict]:
    """Robustness rows. A missing box is omitted, never faked."""
    rows = []
    for box in SENSITIVITY_BOXES:
        if box not in ra.boxes:
            continue
        row = sensitivity_row(box, DATASET["label"], ra.boxes[box])
        if row is not None:
            rows.append(row)
    return rows


def sensitivity_row(box: str, dataset: str, annual: pd.DataFrame) -> dict | None:
    """One robustness row from an annual frame (year, total_mm, complete). None if too few years."""
    sub = complete_only(annual)
    if len(sub) < stats.MIN_N:
        return None
    a = analyse_series(sub["year"].to_numpy(), sub["total_mm"].to_numpy())
    return {
        "box": box,
        "dataset": dataset,
        "n_years": a["n"],
        "p": round(a["p"], 3),
        "sen_slope_mm_per_year": round(a["slope"], 1),
        "sen_ci95": [round(a["low"], 1), round(a["high"], 1)],
        "verdict": a["verdict"],
    }


def build_spatial(cells: pd.DataFrame | None) -> dict:
    """Exploratory per-cell trend map. Unavailable under plan B (cells is None)."""
    if cells is None:
        return {
            "exploratory": True,
            "available": False,
            "n_cells": 0,
            "alpha": ALPHA,
            "expected_false_positives": 0,
            "n_significant": 0,
            "cells": [],
        }
    cells = complete_only(cells)
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
