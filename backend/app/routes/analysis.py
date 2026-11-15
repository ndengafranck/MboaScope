"""POST /api/analysis/trends, POST /api/analysis/spatial, GET /api/analysis/history. Owner: Developer A."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.models import database as db
from app.schemas.analysis import InvestigationLog, SpatialResponse, TrendsResponse
from app.schemas.common import InvestigationRequest
from app.services import investigation

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/trends", response_model=TrendsResponse)
def trends(req: InvestigationRequest) -> TrendsResponse:
    inv = investigation.run(req.region_id, req.start_year, req.end_year)
    analysis = investigation.require_analysis(inv)
    h = analysis["headline"]
    primary = h["mk_hamed_rao"] if h["mk_test_used"] == "hamed_rao" else h["mk_original"]
    log_id = db.log_investigation({
        "region_id": inv.region.id,
        "start_year": inv.start_year,
        "end_year": inv.end_year,
        "verdict": h["verdict"],
        "p": primary["p"],
        "sen_slope_mm_per_year": h["sen_slope_mm_per_year"],
        "is_mock": inv.is_mock,
    })
    return TrendsResponse(is_mock=inv.is_mock, investigation_id=log_id, **analysis)


@router.post("/spatial", response_model=SpatialResponse)
def spatial(req: InvestigationRequest) -> SpatialResponse:
    inv = investigation.run(req.region_id, req.start_year, req.end_year)
    return SpatialResponse(
        is_mock=inv.is_mock,
        region_id=inv.region.id,
        grid_bounds=inv.region.grid_bounds,
        **inv.spatial,
    )


@router.get("/history", response_model=list[InvestigationLog])
def history(limit: int = Query(20, ge=1, le=200)) -> list[InvestigationLog]:
    return [InvestigationLog(**row) for row in db.recent_investigations(limit)]
