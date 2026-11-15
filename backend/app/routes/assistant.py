"""POST /api/ai/interpret. Owner: Developer B."""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from app.schemas.ai import Explanation, InterpretRequest, InterpretResponse, Suggestion
from app.services import investigation
from app.services.ai import interpreter

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/interpret", response_model=InterpretResponse)
async def interpret(req: InterpretRequest) -> InterpretResponse:
    inv = investigation.run(req.region_id, req.start_year, req.end_year)
    analysis = investigation.require_analysis(inv)
    # Gemini calls block for seconds: keep them off the event loop.
    payload, notes = await run_in_threadpool(interpreter.interpret, analysis, req.use_llm)
    return InterpretResponse(
        is_mock=inv.is_mock,
        region_id=inv.region.id,
        explanation=Explanation(**payload),
        notes=notes,
        suggestions=[Suggestion(**s) for s in interpreter.suggest_investigations(analysis)],
    )
