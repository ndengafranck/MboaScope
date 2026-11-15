"""Regional extraction and annual totals. Owner: Developer A (GIS tasks).

Rules (docs/methodology.md):
- box monthly value = plain mean of the cells whose centres fall inside the box;
- annual total = sum of 12 monthly totals; a year with fewer than 12 months is
  marked incomplete, excluded from the tests and listed. No gap filling.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from app.core.config import BOX_SIZES, HEADLINE_BOX
from app.services.gis.regions import Region
from app.services.nasa.precipitation import RegionInput

TOL = 1e-6
VALID_CELL_COUNTS = (1, 9, 25)
MIN_PLAUSIBLE_MM = 300  # Far North semi-arid
MAX_PLAUSIBLE_MM = 12000  # Mount Cameroon foothills


def cells_in_box(df: pd.DataFrame, bounds: list[float], expected: int | None = None) -> pd.DataFrame:
    """Rows whose cell centre falls inside [south, north, west, east].

    `expected` is the cell count the box must contain (side x side); a missing
    cell means a partial download, and must fail loudly rather than shrink the box.
    """
    south, north, west, east = bounds
    mask = (
        (df["lat"] > south - TOL) & (df["lat"] < north + TOL)
        & (df["lon"] > west - TOL) & (df["lon"] < east + TOL)
    )
    sub = df[mask]
    n_cells = len(sub[["lat", "lon"]].drop_duplicates())
    if expected is not None and n_cells != expected:
        raise ValueError(f"box {bounds} contains {n_cells} cells, expected {expected}")
    if n_cells not in VALID_CELL_COUNTS:
        raise ValueError(f"box {bounds} contains {n_cells} cells, expected 1, 9 or 25")
    return sub


def to_annual(monthly: pd.DataFrame) -> pd.DataFrame:
    """One row per month (year, mm) to one row per year: year, total_mm, months_present, complete."""
    out = (
        monthly.groupby("year")["mm"]
        .agg(total_mm="sum", months_present="count")
        .reset_index()
        .sort_values("year")
    )
    out["complete"] = out["months_present"] == 12
    return out.reset_index(drop=True)


def box_annual(df_mm: pd.DataFrame, bounds: list[float], expected: int | None = None) -> pd.DataFrame:
    sub = cells_in_box(df_mm, bounds, expected)
    monthly = sub.groupby(["month", "year"], as_index=False)["mm"].mean()
    return to_annual(monthly)


def cell_annual(df_mm: pd.DataFrame) -> pd.DataFrame:
    """Per-cell annual totals: lat, lon, year, total_mm, months_present, complete."""
    cells = (
        df_mm.groupby(["lat", "lon", "year"])["mm"]
        .agg(total_mm="sum", months_present="count")
        .reset_index()
    )
    cells["complete"] = cells["months_present"] == 12
    return cells


def implausible_years(annual: pd.DataFrame) -> list[int]:
    """Complete years outside the plausible range: almost always a unit error."""
    bad = annual[
        annual["complete"]
        & ((annual["total_mm"] < MIN_PLAUSIBLE_MM) | (annual["total_mm"] > MAX_PLAUSIBLE_MM))
    ]
    return [int(y) for y in bad["year"]]


def climatology(df_mm: pd.DataFrame, bounds: list[float]) -> list[dict]:
    """Mean monthly total (mm) per calendar month over the box: the seasonal cycle."""
    sub = cells_in_box(df_mm, bounds)
    monthly = sub.groupby(["month", "year"], as_index=False)["mm"].mean()
    monthly["m"] = monthly["month"].str[5:7].astype(int)
    clim = monthly.groupby("m")["mm"].mean()
    return [{"month": int(m), "mean_mm": int(round(v))} for m, v in clim.items()]


@dataclass
class RegionAnnual:
    """Everything the analytics module needs for one region and period."""

    region: Region
    kind: str  # "region" or "box"
    boxes: dict[str, pd.DataFrame]  # box id -> annual frame
    cells: pd.DataFrame | None  # per-cell annual totals, None under plan B
    climatology: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def build_region_annual(region: Region, data: RegionInput, start_year: int, end_year: int) -> RegionAnnual:
    df = data.monthly[(data.monthly["year"] >= start_year) & (data.monthly["year"] <= end_year)]
    warnings: list[str] = []
    if data.kind == "region":
        boxes = {box: box_annual(df, region.box_bounds(box), side * side) for box, side in BOX_SIZES.items()}
        cells = cell_annual(cells_in_grid(df, region))
        clim = climatology(df, region.box_bounds(HEADLINE_BOX))
    else:
        monthly = df[df["box"] == HEADLINE_BOX][["month", "year", "mm"]]
        boxes = {HEADLINE_BOX: to_annual(monthly)}
        cells = None
        monthly = monthly.assign(m=monthly["month"].str[5:7].astype(int))
        clim = [{"month": int(m), "mean_mm": int(round(v))} for m, v in monthly.groupby("m")["mm"].mean().items()]
    for box, annual in boxes.items():
        bad = implausible_years(annual)
        if bad:
            warnings.append(f"{box}: implausible annual totals in {bad}, check units")
    return RegionAnnual(region=region, kind=data.kind, boxes=boxes, cells=cells, climatology=clim, warnings=warnings)


def cells_in_grid(df: pd.DataFrame, region: Region) -> pd.DataFrame:
    south, north, west, east = region.grid_bounds
    mask = (
        (df["lat"] > south - TOL) & (df["lat"] < north + TOL)
        & (df["lon"] > west - TOL) & (df["lon"] < east + TOL)
    )
    return df[mask]


def annual_points(annual: pd.DataFrame) -> list[dict]:
    """Annual frame to API points, millimetres rounded to 0 decimals."""
    return [
        {
            "year": int(r.year),
            "total_mm": int(round(r.total_mm)),
            "months_present": int(r.months_present),
            "complete": bool(r.complete),
        }
        for r in annual.itertuples()
    ]
