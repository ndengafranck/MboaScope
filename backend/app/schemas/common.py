"""Shared request and envelope models. Owner: Developer A. The API contract is docs/api.md."""
from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.core.config import API_VERSION, END_YEAR, START_YEAR


class InvestigationRequest(BaseModel):
    """Body of every POST endpoint: which region, which years."""

    region_id: str = Field(examples=["douala"])
    start_year: int = Field(START_YEAR, ge=START_YEAR, le=END_YEAR)
    end_year: int = Field(END_YEAR, ge=START_YEAR, le=END_YEAR)


class Envelope(BaseModel):
    """Fields every response carries."""

    api_version: str = API_VERSION
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    is_mock: bool


class Provenance(BaseModel):
    dataset: str
    short_name: str
    version: str
    doi: str
    access_method: str  # mock | earthaccess | giovanni_csv
    source_units: str
    period: list[str]  # [YYYY-MM, YYYY-MM] available for this region
    granule_count: int
    notes: list[str]


class ErrorResponse(BaseModel):
    detail: str
