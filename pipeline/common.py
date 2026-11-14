"""Shared helpers. Owner: Lead."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "1.0"

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"
WEB_DATA = ROOT / "web" / "public" / "data"
SOURCES_PATH = INTERIM / "sources.json"


def read_sources(path: Path = SOURCES_PATH) -> dict[str, Any]:
    """Read data/interim/sources.json (written by the Data role)."""
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run `make mock` or the Data fetch first.")
    return json.loads(path.read_text(encoding="utf-8"))


def is_mock_run(path: Path = SOURCES_PATH) -> bool:
    """True when sources.json says access_method is mock."""
    return read_sources(path).get("access_method") == "mock"


def write_json(path: Path | str, payload: dict[str, Any], is_mock: bool) -> None:
    """Write a web JSON file with the contract envelope.

    Adds contract_version, generated_at (UTC ISO 8601) and is_mock in front of
    the payload keys.
    """
    envelope = {
        "contract_version": CONTRACT_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "is_mock": bool(is_mock),
    }
    body = {**envelope, **{k: v for k, v in payload.items() if k not in envelope}}
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(body, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
