"""Regions and rainfall series. Owner: Developer A."""
from __future__ import annotations

from pydantic import BaseModel

from app.schemas.common import Envelope, Provenance


class BoxInfo(BaseModel):
    label: str
    bounds: list[float]  # [south, north, west, east]


class RegionOut(BaseModel):
    id: str
    name: str
    admin_region: str
    centre: list[float]  # [lat, lon]
    coastal: bool
    verified: bool  # False until the study box has been checked on a map
    boxes: dict[str, BoxInfo]
    grid_bounds: list[float]
    has_data: bool
    access_method: str | None
    period: list[str] | None


class RegionsResponse(BaseModel):
    regions: list[RegionOut]


class AnnualPoint(BaseModel):
    year: int
    total_mm: int
    months_present: int
    complete: bool


class ClimatologyPoint(BaseModel):
    month: int  # 1-12
    mean_mm: int


class RainfallSeriesResponse(Envelope):
    region_id: str
    region_name: str
    box: str
    box_label: str
    bounds: list[float]
    period: list[int]  # [start_year, end_year]
    years: list[AnnualPoint]
    excluded_years: list[int]
    climatology: list[ClimatologyPoint]
    warnings: list[str]
    provenance: Provenance
