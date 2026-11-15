"""One rainfall investigation = region + period, run through NASA -> GIS -> analytics.

Owner: Developer A. Routes call this module only; they never touch the
services below it directly. Results are cached in memory per
(region, period, data version), so the frontend can call the four endpoints
for the same investigation without recomputing.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from app.core.config import END_YEAR, MIN_YEARS, START_YEAR
from app.core.errors import InvalidPeriod, NoDataForRegion, NotEnoughYears
from app.models import database as db
from app.services.analytics import trends
from app.services.gis.regions import Region, get_region
from app.services.gis.spatial import RegionAnnual, build_region_annual
from app.services.nasa.precipitation import load_region_input


@dataclass
class Investigation:
    region: Region
    start_year: int
    end_year: int
    source: dict
    annual: RegionAnnual
    analysis: dict | None  # {"headline": ..., "sensitivity": [...]}, None if too few complete years
    spatial: dict

    @property
    def is_mock(self) -> bool:
        return self.source["access_method"] == "mock"


def validate_period(start_year: int, end_year: int, source: dict | None = None) -> None:
    lo, hi = START_YEAR, END_YEAR
    if source:
        lo = max(lo, int(source["period_start"][:4]))
        hi = min(hi, int(source["period_end"][:4]))
    if start_year > end_year:
        raise InvalidPeriod("start_year must not be after end_year")
    if start_year < lo or end_year > hi:
        raise InvalidPeriod(f"period must lie within {lo}-{hi} for this region")
    if end_year - start_year + 1 < MIN_YEARS:
        raise NotEnoughYears(f"choose at least {MIN_YEARS} years; the trend tests have no power below that")


def run(region_id: str, start_year: int = START_YEAR, end_year: int = END_YEAR) -> Investigation:
    region = get_region(region_id)
    source = db.get_source(region.id)
    if source is None:
        raise NoDataForRegion(f"no rainfall data ingested for {region.id!r} yet")
    validate_period(start_year, end_year, source)
    return _run_cached(region.id, start_year, end_year, source["updated_at"])


@lru_cache(maxsize=256)
def _run_cached(region_id: str, start_year: int, end_year: int, _data_version: str) -> Investigation:
    region = get_region(region_id)
    data = load_region_input(region_id)
    annual = build_region_annual(region, data, start_year, end_year)
    try:
        analysis = {"headline": trends.build_headline(annual), "sensitivity": trends.build_sensitivity(annual)}
    except ValueError:
        analysis = None
    return Investigation(
        region=region,
        start_year=start_year,
        end_year=end_year,
        source=data.source,
        annual=annual,
        analysis=analysis,
        spatial=trends.build_spatial(annual.cells),
    )


def require_analysis(inv: Investigation) -> dict:
    if inv.analysis is None:
        raise NotEnoughYears(
            f"fewer than {MIN_YEARS} complete years in {inv.start_year}-{inv.end_year} for {inv.region.id}"
        )
    return inv.analysis


def clear_cache() -> None:
    _run_cached.cache_clear()
