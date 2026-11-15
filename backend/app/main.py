"""FastAPI application. Owner: Developer A.

Run: uvicorn app.main:app --reload   (from the backend/ folder)
Docs: http://127.0.0.1:8000/docs
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import API_VERSION, get_settings
from app.core.errors import MboaScopeError
from app.routes import analysis, assistant, health, rainfall, regions

app = FastAPI(
    title="MboaScope API",
    version=API_VERSION,
    description="Historical rainfall trends for study regions in Cameroon, from NASA GPM IMERG.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(MboaScopeError)
async def domain_error(_: Request, exc: MboaScopeError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


for module in (health, regions, rainfall, analysis, assistant):
    app.include_router(module.router, prefix="/api")
