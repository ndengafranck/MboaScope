"""POST /api/rainfall/series. Owner: Developer A."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.config import DATASET, HEADLINE_BOX
from app.schemas.common import InvestigationRequest, Provenance
from app.schemas.rainfall import RainfallSeriesResponse
from app.services import investigation
from app.services.gis.spatial import annual_points

router = APIRouter(prefix="/rainfall", tags=["rainfall"])


def provenance(source: dict) -> Provenance:
    return Provenance(
        dataset=DATASET["name"],
        short_name=DATASET["short_name"],
        version=DATASET["version"],
        doi=DATASET["doi"],
        access_method=source["access_method"],
        source_units=source["source_units"],
        period=[source["period_start"], source["period_end"]],
        granule_count=source["granule_count"],
        notes=source["notes"],
    )


@router.post("/series", response_model=RainfallSeriesResponse)
def rainfall_series(req: InvestigationRequest) -> RainfallSeriesResponse:
    inv = investigation.run(req.region_id, req.start_year, req.end_year)
    annual = inv.annual.boxes[HEADLINE_BOX]
    return RainfallSeriesResponse(
        is_mock=inv.is_mock,
        region_id=inv.region.id,
        region_name=inv.region.name,
        box=HEADLINE_BOX,
        box_label=inv.region.box_label(HEADLINE_BOX),
        bounds=inv.region.box_bounds(HEADLINE_BOX),
        period=[inv.start_year, inv.end_year],
        years=annual_points(annual),
        excluded_years=[int(y) for y in annual.loc[~annual["complete"], "year"]],
        climatology=inv.annual.climatology,
        warnings=inv.annual.warnings,
        provenance=provenance(inv.source),
    )
