"""Optional cross-check: GPCP V3.3 monthly for the study regions. Owner: Developer A (task A8).

CLI: python -m app.cli fetch-gpcp [--region douala ...] [--start 2001-01] [--end 2024-12] [--limit N]

GPCP is a different product (0.5 degree grid, different inputs). It is stored in
box_observations under its own box name and gives one extra row in the
sensitivity table. It is never joined to the IMERG series and never becomes the headline.

For each region we keep the one GPCP cell that contains the IMERG centre cell
(about 55 km across, larger than the 3 x 3 IMERG box).

Needs: pip install -r backend/requirements-fetch.txt, and NASA Earthdata access as for IMERG.
"""
from __future__ import annotations

import math
from pathlib import Path

from app.core.config import END_YEAR, RAW_DIR, START_YEAR
from app.models import database as db
from app.services.gis.regions import Region, load_regions
from app.services.nasa import fetch_imerg

GPCP = {
    "name": "GPCP Precipitation Level 3 Monthly 0.5-Degree V3.3",
    "short_name": "GPCPMON",
    "version": "3.3",
    "doi": "10.5067/MEASURES/GPCP/DATA306",
    "variable": "sat_gauge_precip",
    "label": "GPCP V3.3",
}
BOX = "gpcp_0.5deg"
CELL = 0.5
DOWNLOAD_DIR = RAW_DIR / "gpcp"


def month_of(name: str) -> str:
    """GPCPMON_L3_200101_V3.3.nc4 -> 2001-01."""
    stamp = name.split("_")[2]
    return f"{stamp[:4]}-{stamp[4:6]}"


def cell_centre(value: float) -> float:
    """Centre of the 0.5 degree GPCP cell that contains `value` (cells are x.25 and x.75)."""
    return math.floor(value / CELL) * CELL + CELL / 2


def read_cell_rates(path, regions: list[Region]) -> tuple[dict[str, float | None], str]:
    """Rate of the GPCP cell containing each region's centre. None for a fill value."""
    import xarray as xr

    ds = xr.open_dataset(path, engine="h5netcdf", decode_times=False)
    da = ds[GPCP["variable"]].squeeze("time", drop=True)
    units = str(da.attrs.get("units", "")).strip()
    out: dict[str, float | None] = {}
    for region in regions:
        lat, lon = cell_centre(region.centre_lat), cell_centre(region.centre_lon)
        cell = da.sel(lat=lat, lon=lon, method="nearest")
        if abs(float(cell["lat"]) - lat) > 1e-3 or abs(float(cell["lon"]) - lon) > 1e-3:
            raise ValueError(f"GPCP grid has no cell centred at ({lat}, {lon})")
        value = float(cell.values)  # xarray applies the fill value as NaN
        out[region.id] = None if math.isnan(value) or value < 0 else value
    ds.close()
    return out, units


def _download(results: list) -> list[str]:
    import earthaccess

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    name = fetch_imerg._name_of
    todo = [g for g in results if not (DOWNLOAD_DIR / name(g)).exists()]
    if todo:
        print(f"download: {len(todo)} files to {DOWNLOAD_DIR} ({len(results) - len(todo)} already there)")
        if fetch_imerg.token_only():
            fetch_imerg.download_with_token(todo, DOWNLOAD_DIR)
        else:
            earthaccess.download(todo, local_path=str(DOWNLOAD_DIR))
    missing = [name(g) for g in results if not (DOWNLOAD_DIR / name(g)).exists()]
    if missing:
        raise SystemExit(f"download incomplete, missing {len(missing)} files. Run the same command again.")
    return [str(DOWNLOAD_DIR / name(g)) for g in results]


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
    fetch_imerg.login()
    results = earthaccess.search_data(
        short_name=GPCP["short_name"], version=GPCP["version"], temporal=(f"{start}-01", f"{end}-28")
    )
    if limit:
        results = results[:limit]
    print(f"fetch-gpcp: {len(results)} granules for {', '.join(r.id for r in regions)}")

    rows: dict[str, list[dict]] = {r.id: [] for r in regions}
    units_seen: set[str] = set()
    for granule, path in zip(results, _download(results)):
        month = month_of(fetch_imerg._name_of(granule))
        rates, units = read_cell_rates(path, regions)
        units_seen.add(units)
        for rid, rate in rates.items():
            if rate is not None:
                rows[rid].append({"month": month, "box": BOX, "rate": rate, "units": units})
    if len(units_seen) > 1:
        raise ValueError(f"granules disagree on units: {units_seen}")
    return {rid: db.replace_box_rows(rid, BOX, r, db_path) for rid, r in rows.items()}
