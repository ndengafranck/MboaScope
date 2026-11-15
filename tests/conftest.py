"""Shared test setup: import the backend package and use a throwaway database."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    """Point the app at an empty SQLite file for one test."""
    from app.core import config
    from app.services import investigation

    db_path = tmp_path / "test.db"
    monkeypatch.setenv("MBOASCOPE_DB", str(db_path))
    config.get_settings.cache_clear()
    investigation.clear_cache()
    yield db_path
    config.get_settings.cache_clear()
    investigation.clear_cache()
