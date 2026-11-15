"""Fetch IMERG V07 monthly per-cell rates for the study regions (plan A). Owner: Developer A (task A1).

CLI: python -m app.cli fetch-imerg [--region douala ...] [--start 2001-01] [--end 2025-12] [--limit N]

STATUS: written from the GES DISC file layout but NOT yet run against NASA.
Task A1 starts with `python -m app.cli inspect-granule` on one granule to confirm
the group, variable, dimension order and units before running the full fetch.

How it works:
1. Log in to NASA Earthdata with EARTHDATA_USERNAME / EARTHDATA_PASSWORD from .env.
2. Search GPM_3IMERGM v07 granules over the union bounding box of the requested regions.
3. Open each granule remotely (earthaccess.open streams byte ranges, so only the
   Cameroon subset is transferred), read Grid/precipitation, keep the 9 x 9 cells of
   each region, and store the rates *as stored* with the file's units attribute.
4. Write one `sources` row per region with access_method "earthaccess".

Needs: pip install -r backend/requirements-fetch.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from app.core.config import DATASET, END_YEAR, START_YEAR
from app.models import database as db
from app.services.gis.regions import Region, load_regions

GROUP = "Grid"
VARIABLE = "precipitation"


def _union_bbox(regions: list[Region]) -> tuple[float, float, float, float]:
    """(west, south, east, north), the order earthaccess expects."""
    bounds = [r.grid_bounds for r in regions]
    return (
        min(b[2] for b in bounds),
        min(b[0] for b in bounds),
        max(b[3] for b in bounds),
        max(b[1] for b in bounds),
    )


def _month_of(granule_name: str) -> str:
    """'3B-MO.MS.MRG.3IMERG.20010101-S000000-E235959.01.V07B.HDF5' -> '2001-01'."""
    stamp = granule_name.split(".3IMERG.")[1][:8]
    return f"{stamp[:4]}-{stamp[4:6]}"


def read_cells(handle, regions: list[Region]) -> tuple[dict[str, pd.DataFrame], str]:
    """Per-region cell rates from one open granule. Returns ({region_id: df(lat, lon, rate)}, units)."""
    import xarray as xr

    ds = xr.open_dataset(handle, group=GROUP, engine="h5netcdf")
    da = ds[VARIABLE].squeeze("time", drop=True)
    units = str(da.attrs.get("units", "")).strip()
    out = {}
    for region in regions:
        south, north, west, east = region.grid_bounds
        sub = da.sel(lat=slice(south, north), lon=slice(west, east)).load()
        df = sub.to_dataframe(name="rate").reset_index()[["lat", "lon", "rate"]]
        df["lat"] = df["lat"].round(2)
        df["lon"] = df["lon"].round(2)
        df = df[np.isfinite(df["rate"]) & (df["rate"] >= 0)]  # fill values dropped, never filled
        out[region.id] = df
    ds.close()
    return out, units


def fetch(
    region_ids: list[str] | None = None,
    start: str = f"{START_YEAR}-01",
    end: str = f"{END_YEAR}-12",
    limit: int | None = None,
    db_path: Path | None = None,
) -> dict[str, int]:
    import earthaccess

    regions_all = load_regions()
    regions = [regions_all[r] for r in (region_ids or list(regions_all))]
    earthaccess.login(strategy="environment")
    results = earthaccess.search_data(
        short_name=DATASET["short_name"],
        version=DATASET["version"],
        temporal=(f"{start}-01", f"{end}-28"),
        bounding_box=_union_bbox(regions),
    )
    if limit:
        results = results[:limit]
    print(f"fetch-imerg: {len(results)} granules for {', '.join(r.id for r in regions)}")

    frames: dict[str, list[pd.DataFrame]] = {r.id: [] for r in regions}
    names: list[str] = []
    units_seen: set[str] = set()
    for granule, handle in zip(results, earthaccess.open(results)):
        name = granule.data_links()[0].rsplit("/", 1)[-1]
        month = _month_of(name)
        cells, units = read_cells(handle, regions)
        units_seen.add(units)
        names.append(name)
        for rid, df in cells.items():
            frames[rid].append(df.assign(month=month, units=units))
        print(f"  {month}: ok ({units})")
    if len(units_seen) != 1:
        raise ValueError(f"granules disagree on units: {units_seen}")

    source_units = next(iter(units_seen))
    stored = {}
    months = sorted(_month_of(n) for n in names)
    for rid, parts in frames.items():
        df = pd.concat(parts, ignore_index=True)[["month", "lat", "lon", "rate", "units"]]
        stored[rid] = db.replace_observations(rid, df, db_path)
        db.upsert_source(
            rid,
            {
                "access_method": "earthaccess",
                "source_units": source_units,
                "period": {"start": months[0], "end": months[-1]},
                "granule_count": len(names),
                "notes": [f"{DATASET['short_name']} v{DATASET['version']} via earthaccess"],
            },
            db_path,
        )
    return stored
