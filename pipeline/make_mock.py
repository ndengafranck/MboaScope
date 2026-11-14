"""Synthetic region data so nobody waits. Owner: Data.

Writes data/interim/region_monthly_rate.csv and sources.json (access_method "mock").
Fixed seed, 9 x 9 cells, 2001-01 to 2025-12, units mm/hr.
"""
from __future__ import annotations

import calendar
import json
import math

import numpy as np
import pandas as pd

from pipeline.common import INTERIM
from pipeline.config import END_YEAR, REGION, START_YEAR

SEED = 20260314
UNITS = "mm/hr"
MEAN_MONTHLY_MM = 308.0  # about 3,700 mm per year before noise
STEP_FACTOR = 1.05  # small step from June 2014


def seasonal(month: int) -> float:
    """Wettest July to September, driest December to February."""
    return 1.0 + 0.85 * math.cos(2 * math.pi * (month - 8) / 12)


def build_mock(start_year: int = START_YEAR, end_year: int = END_YEAR) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    south, north, west, east = REGION
    lats = np.round(np.arange(south + 0.05, north, 0.1), 2)
    lons = np.round(np.arange(west + 0.05, east, 0.1), 2)
    year_factor = {y: float(np.clip(rng.normal(1.0, 0.08), 0.85, 1.15)) for y in range(start_year, end_year + 1)}
    cell_factor = {(la, lo): 1.0 + 0.05 * (la - 4.05) + float(rng.normal(0, 0.02)) for la in lats for lo in lons}
    rows = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            days = calendar.monthrange(year, month)[1]
            step = STEP_FACTOR if (year, month) >= (2014, 6) else 1.0
            base = MEAN_MONTHLY_MM * seasonal(month) * year_factor[year] * step
            month_noise = float(np.clip(rng.normal(1.0, 0.12), 0.6, 1.4))
            for la in lats:
                for lo in lons:
                    cell_noise = float(np.clip(rng.normal(1.0, 0.05), 0.8, 1.2))
                    total = base * month_noise * cell_factor[(la, lo)] * cell_noise
                    rows.append((f"{year}-{month:02d}", float(la), float(lo), round(total / (24 * days), 4), UNITS))
    return pd.DataFrame(rows, columns=["month", "lat", "lon", "rate", "units"])


def main() -> None:
    INTERIM.mkdir(parents=True, exist_ok=True)
    df = build_mock()
    # lat/lon need exactly 2 decimals; rate keeps 4.
    df.assign(lat=df["lat"].map("{:.2f}".format), lon=df["lon"].map("{:.2f}".format), rate=df["rate"].map("{:.4f}".format)).to_csv(
        INTERIM / "region_monthly_rate.csv", index=False
    )
    months = sorted(df["month"].unique())
    sources = {
        "access_method": "mock",
        "source_units": UNITS,
        "period": {"start": months[0], "end": months[-1]},
        "granules": [{"id": f"mock-{m}", "month": m} for m in months],
        "notes": ["Synthetic data from pipeline/make_mock.py. Not NASA data."],
    }
    (INTERIM / "sources.json").write_text(json.dumps(sources, indent=2) + "\n", encoding="utf-8")
    print(f"mock: {len(df)} rows, {len(months)} months")


if __name__ == "__main__":
    main()
