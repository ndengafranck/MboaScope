"""GET /api/regions. Owner: Developer A."""
from __future__ import annotations

from fastapi import APIRouter

from app.models import database as db
from app.schemas.rainfall import RegionOut, RegionsResponse
from app.services.gis.regions import load_regions

router = APIRouter(tags=["regions"])


@router.get("/regions", response_model=RegionsResponse)
def list_regions() -> RegionsResponse:
    sources = db.all_sources()
    out = []
    for region in load_regions().values():
        src = sources.get(region.id)
        out.append(RegionOut(
            **region.to_dict(),
            has_data=src is not None,
            access_method=src["access_method"] if src else None,
            period=[src["period_start"], src["period_end"]] if src else None,
        ))
    return RegionsResponse(regions=out)
