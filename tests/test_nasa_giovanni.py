"""Tests for app/services/nasa/giovanni.py. Owner: Developer A. No network."""
from __future__ import annotations

import pytest

from app.models import database as db
from app.services.nasa import giovanni as import_giovanni

SAMPLE = """title,Time Series, Area-Averaged of Merged satellite-gauge precipitation estimate monthly 0.1 deg. [GPM GPM_3IMERGM v07] mm/hr over 2001-01-01 - 2001-04-30, Region 9.6E, 3.9N, 9.9E, 4.2N
User Start Date,2001-01-01T00:00:00Z
User End Date,2001-04-30T23:59:59Z
Bounding Box,"9.6,3.9,9.9,4.2"
Fill Value (mean_GPM_3IMERGM_07_precipitation),-9999.9

time,mean_GPM_3IMERGM_07_precipitation
2001-01-01,0.0566
2001-02-01T00:00:00Z,0.0912
2001-03-01,-9999.9
2001-04-01,0.2731
"""


def write_sample(tmp_path):
    src = tmp_path / "g.csv"
    src.write_text(SAMPLE, encoding="utf-8")
    return src


def test_parses_metadata_header_and_rows(tmp_path, tmp_db):
    import_giovanni.run(write_sample(tmp_path), "douala")
    df = db.read_box_observations("douala")
    assert df["month"].tolist() == ["2001-01", "2001-02", "2001-04"]  # fill value dropped, not filled
    assert df.iloc[0].to_dict() == {"month": "2001-01", "box": "box_3x3", "rate": 0.0566, "units": "mm/hr"}


def test_sources_untouched_without_activate(tmp_path, tmp_db):
    db.upsert_source("douala", {"access_method": "earthaccess", "source_units": "mm/hr",
                                "period": {"start": "2001-01", "end": "2025-12"}})
    import_giovanni.run(write_sample(tmp_path), "douala")
    assert db.get_source("douala")["access_method"] == "earthaccess"


def test_activate_writes_plan_b_sources(tmp_path, tmp_db):
    import_giovanni.run(write_sample(tmp_path), "douala", activate=True)
    source = db.get_source("douala")
    assert source["access_method"] == "giovanni_csv"
    assert source["source_units"] == "mm/hr"
    assert (source["period_start"], source["period_end"]) == ("2001-01", "2001-04")
    assert "area average computed by Giovanni" in source["notes"]


def test_missing_units_requires_flag():
    text = SAMPLE.replace(" mm/hr", "")
    with pytest.raises(ValueError, match="--units"):
        import_giovanni.parse(text)
    rows, units = import_giovanni.parse(text, units="mm/hr")
    assert units == "mm/hr" and len(rows) == 3


def test_no_header_raises():
    with pytest.raises(ValueError, match="time"):
        import_giovanni.parse("a,b\n1,2\n")
