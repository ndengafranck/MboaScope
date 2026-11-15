"""GET /api/health. Owner: Developer A."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.config import API_VERSION
from app.models import database as db

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    sources = db.all_sources()
    return {
        "status": "ok",
        "api_version": API_VERSION,
        "regions_with_data": sorted(sources),
        "is_mock": any(s["access_method"] == "mock" for s in sources.values()),
    }
