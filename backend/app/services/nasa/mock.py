"""Synthetic monthly rates for every study region, so nobody waits for NASA. Owner: Developer A.

Deterministic per region (seed from the region id). 9 x 9 cells around each
centre, 2001-01 to END_YEAR-12, units mm/hr, stored with access_method "mock".
Every API response built on this data says is_mock: true.

The climate numbers below are rough placeholders chosen only so the demo looks
plausible (wet coast, dry north, some regions with a built-in trend or step).
They are NOT findings and must never be quoted.
"""
from __future__ import annotations

import calendar
import math
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

from app.core.config import END_YEAR, START_YEAR
from app.models import database as db
from app.services.gis.regions import Region, load_regions

UNITS = "mm/hr"

# region id: (mean annual mm, wettest month, built-in trend in % per decade, step factor from June 2014)
PROFILES = {
    "douala": (3700, 8, 0.0, 1.05),
    "buea": (3000, 8, 0.0, 1.00),
    "yaounde": (1600, 10, 3.0, 1.00),
    "bamenda": (2400, 8, 0.0, 1.00),
    "bafoussam": (1800, 9, -2.5, 1.00),
    "ebolowa": (1800, 10, 0.0, 1.00),
    "bertoua": (1550, 9, 0.0, 1.06),
    "ngaoundere": (1500, 8, 0.0, 1.00),
    "garoua": (1000, 8, -4.0, 1.00),
    "maroua": (800, 8, 4.5, 1.00),
}
DEFAULT_PROFILE = (1600, 8, 0.0, 1.0)


def seasonal(month: int, peak: int) -> float:
    return 1.0 + 0.85 * math.cos(2 * math.pi * (month - peak) / 12)


def build_mock(region: Region, start_year: int = START_YEAR, end_year: int = END_YEAR) -> pd.DataFrame:
    mean_annual, peak, trend_pct, step_factor = PROFILES.get(region.id, DEFAULT_PROFILE)
    rng = np.random.default_rng(zlib.crc32(region.id.encode()))
    cells = region.grid_cells()
    year_factor = {y: float(np.clip(rng.normal(1.0, 0.08), 0.8, 1.2)) for y in range(start_year, end_year + 1)}
    cell_factor = {c: 1.0 + float(rng.normal(0, 0.03)) for c in cells}
    rows = []
    for year in range(start_year, end_year + 1):
        trend = 1.0 + trend_pct / 100 * (year - start_year) / 10
        for month in range(1, 13):
            days = calendar.monthrange(year, month)[1]
            step = step_factor if (year, month) >= (2014, 6) else 1.0
            base = mean_annual / 12 * seasonal(month, peak) * year_factor[year] * trend * step
            month_noise = float(np.clip(rng.normal(1.0, 0.12), 0.6, 1.4))
            for lat, lon in cells:
                cell_noise = float(np.clip(rng.normal(1.0, 0.05), 0.8, 1.2))
                total = max(base * month_noise * cell_factor[(lat, lon)] * cell_noise, 0.0)
                rows.append((f"{year}-{month:02d}", lat, lon, round(total / (24 * days), 4), UNITS))
    return pd.DataFrame(rows, columns=["month", "lat", "lon", "rate", "units"])


def seed_region(region: Region, db_path: Path | None = None) -> int:
    df = build_mock(region)
    n = db.replace_observations(region.id, df, db_path)
    months = sorted(df["month"].unique())
    db.upsert_source(
        region.id,
        {
            "access_method": "mock",
            "source_units": UNITS,
            "period": {"start": months[0], "end": months[-1]},
            "granule_count": len(months),
            "notes": ["Synthetic data from app/services/nasa/mock.py. Not NASA data."],
        },
        db_path,
    )
    return n


def seed_all(region_ids: list[str] | None = None, db_path: Path | None = None) -> dict[str, int]:
    regions = load_regions()
    ids = region_ids or list(regions)
    return {rid: seed_region(regions[rid], db_path) for rid in ids}
