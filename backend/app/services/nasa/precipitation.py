"""Monthly precipitation for one study region, ready for the GIS module. Owner: Developer A.

The NASA layer stores rates exactly as the files give them (see database.py).
This module reads them back, decides which input applies (the `sources`
row is the only switch, never "which table has rows"), and converts each
monthly mean rate to a monthly total in millimetres.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd

from app.core.errors import NoDataForRegion
from app.models import database as db
from app.services.nasa import units

InputKind = Literal["region", "box"]


@dataclass
class RegionInput:
    kind: InputKind  # "region": per-cell grid (plan A, mock); "box": Giovanni box average (plan B)
    monthly: pd.DataFrame  # month, year, mm (+ lat, lon for region; + box for box)
    source: dict

    @property
    def is_mock(self) -> bool:
        return self.source["access_method"] == "mock"


def add_mm(df: pd.DataFrame) -> pd.DataFrame:
    """Add year and the monthly total in mm to every row (rate x hours or days in that month)."""
    df = df.copy()
    df["year"] = df["month"].str[:4].astype(int)
    month = df["month"].str[5:7].astype(int)
    df["mm"] = [
        units.monthly_total_mm(r, u, y, m)
        for r, u, y, m in zip(df["rate"], df["units"], df["year"], month)
    ]
    return df


def load_region_input(region_id: str, db_path: Path | None = None) -> RegionInput:
    source = db.get_source(region_id, db_path)
    if source is None:
        raise NoDataForRegion(
            f"no rainfall data ingested for {region_id!r} yet: run `python -m app.cli seed-mock` "
            "or a NASA import for this region"
        )
    method = source["access_method"]
    if method in ("mock", "earthaccess"):
        raw, kind = db.read_observations(region_id, db_path), "region"
    elif method == "giovanni_csv":
        raw, kind = db.read_box_observations(region_id, db_path), "box"
    else:
        raise ValueError(f"unknown access_method {method!r} for {region_id}")
    if raw.empty:
        raise NoDataForRegion(f"{region_id}: sources says {method} but no rows are stored")
    return RegionInput(kind=kind, monthly=add_mm(raw), source=source)
