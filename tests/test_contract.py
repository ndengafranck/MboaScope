"""Contract tests. Owner: Lead.

Validates every web JSON file against docs/contract/*.schema.json and checks the
interim CSV headers when the files exist.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "docs" / "contract"
WEB_DATA = ROOT / "web" / "public" / "data"
INTERIM = ROOT / "data" / "interim"

NAMES = ["annual", "analysis", "spatial", "explanation", "provenance"]

CSV_HEADERS = {
    "region_monthly_rate.csv": ["month", "lat", "lon", "rate", "units"],
    "box_monthly_rate.csv": ["month", "box", "rate", "units"],
    "gpcp_box_monthly_rate.csv": ["month", "box", "rate", "units"],
    "annual_box.csv": ["dataset", "box", "year", "total_mm", "months_present", "complete"],
    "annual_cell.csv": ["lat", "lon", "year", "total_mm", "complete"],
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", NAMES)
def test_schema_is_valid(name):
    Draft202012Validator.check_schema(load(SCHEMAS / f"{name}.schema.json"))


@pytest.mark.parametrize("name", NAMES)
def test_web_json_matches_schema(name):
    path = WEB_DATA / f"{name}.json"
    assert path.exists(), f"{path} is missing"
    schema = load(SCHEMAS / f"{name}.schema.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(load(path)), key=lambda e: list(e.path))
    assert not errors, "\n".join(f"{list(e.path)}: {e.message}" for e in errors)


def test_mock_flag_is_consistent():
    flags = {name: load(WEB_DATA / f"{name}.json")["is_mock"] for name in NAMES}
    assert len(set(flags.values())) == 1, f"mixed mock and real files: {flags}"


@pytest.mark.parametrize("filename", sorted(CSV_HEADERS))
def test_interim_csv_headers(filename):
    path = INTERIM / filename
    if not path.exists():
        pytest.skip(f"{filename} not present")
    with path.open(encoding="utf-8", newline="") as handle:
        assert next(csv.reader(handle)) == CSV_HEADERS[filename]
