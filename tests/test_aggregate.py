"""Tests for pipeline/aggregate.py (issue #14). Synthetic data, no network."""
import json
from pathlib import Path

import jsonschema
import pandas as pd
import pytest

from pipeline import aggregate
from pipeline.config import BOXES

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "docs" / "contract" / "annual.schema.json"
LATS = [3.95, 4.05, 4.15]
LONS = [9.65, 9.75, 9.85]


def tiny_region(year: int = 2025, drop_month: int | None = None) -> pd.DataFrame:
    """9 cells inside box_3x3 with rates 1 to 9 mm/hr for every month."""
    rows = []
    rate = 1.0
    cells = []
    for lat in LATS:
        for lon in LONS:
            cells.append((lat, lon, rate))
            rate += 1
    for m in range(1, 13):
        if m == drop_month:
            continue
        for lat, lon, r in cells:
            rows.append({"month": f"{year}-{m:02d}", "lat": lat, "lon": lon, "rate": r, "units": "mm/hr"})
    return pd.DataFrame(rows)


def test_exact_box_mean():
    annual = aggregate.box_annual(aggregate.add_mm(tiny_region()), BOXES["box_3x3"]["bounds"])
    # mean rate is 5 mm/hr, 2025 has 365 days
    assert annual.loc[0, "total_mm"] == pytest.approx(5 * 24 * 365)
    assert bool(annual.loc[0, "complete"]) is True


def test_missing_month_excludes_year():
    annual = aggregate.box_annual(aggregate.add_mm(tiny_region(drop_month=7)), BOXES["box_3x3"]["bounds"])
    assert int(annual.loc[0, "months_present"]) == 11
    assert bool(annual.loc[0, "complete"]) is False
    assert aggregate.box_json(annual, "box_3x3")["excluded_years"] == [2025]


def test_box_cell_counts_on_full_region():
    lats = [round(3.65 + 0.1 * i, 2) for i in range(9)]
    lons = [round(9.35 + 0.1 * j, 2) for j in range(9)]
    grid = pd.DataFrame([(a, o) for a in lats for o in lons], columns=["lat", "lon"])
    counts = {
        box: len(aggregate.cells_in_box(grid, cfg["bounds"])[["lat", "lon"]].drop_duplicates())
        for box, cfg in BOXES.items()
    }
    assert counts == {"box_1x1": 1, "box_3x3": 9, "box_5x5": 25}


def test_wrong_box_raises():
    grid = pd.DataFrame({"lat": [3.95, 4.05], "lon": [9.65, 9.65]})
    with pytest.raises(ValueError):
        aggregate.cells_in_box(grid, BOXES["box_3x3"]["bounds"])


def test_complete_written_as_lowercase_text():
    annual = aggregate.box_annual(aggregate.add_mm(tiny_region()), BOXES["box_3x3"]["bounds"])
    assert aggregate.box_rows(annual, "box_3x3", "IMERG V07")[0]["complete"] == "true"
    cells = aggregate.cell_annual(aggregate.add_mm(tiny_region(drop_month=1)))
    assert set(cells["complete"]) == {"false"}


def write_sources(folder: Path, method: str) -> None:
    (folder / "sources.json").write_text(json.dumps({"access_method": method}), encoding="utf-8")


def test_run_region_end_to_end(tmp_path):
    write_sources(tmp_path, "mock")
    tiny_region().to_csv(tmp_path / "region_monthly_rate.csv", index=False)
    aggregate.run(tmp_path, tmp_path)
    box = pd.read_csv(tmp_path / "annual_box.csv", dtype={"complete": str})
    assert list(box.columns) == aggregate.BOX_COLUMNS
    assert set(box["complete"]) == {"true"}
    assert (tmp_path / "annual_cell.csv").exists()
    annual = json.loads((tmp_path / "annual.json").read_text(encoding="utf-8"))
    jsonschema.validate(annual, json.loads(SCHEMA.read_text(encoding="utf-8")))
    assert annual["is_mock"] is True
    assert annual["boxes"]["box_3x3"]["years"][0]["total_mm"] == 43800


def test_plan_b_uses_box_file_only(tmp_path):
    write_sources(tmp_path, "giovanni_csv")
    tiny_region().to_csv(tmp_path / "region_monthly_rate.csv", index=False)  # must be ignored
    pd.DataFrame({
        "month": [f"2025-{m:02d}" for m in range(1, 13)],
        "box": "box_3x3", "rate": 0.5, "units": "mm/hr",
    }).to_csv(tmp_path / "box_monthly_rate.csv", index=False)
    aggregate.run(tmp_path, tmp_path)
    annual = json.loads((tmp_path / "annual.json").read_text(encoding="utf-8"))
    assert list(annual["boxes"]) == ["box_3x3"]
    assert annual["boxes"]["box_3x3"]["years"][0]["total_mm"] == round(0.5 * 24 * 365)
    assert not (tmp_path / "annual_cell.csv").exists()


def test_gpcp_rows_go_to_csv_not_json(tmp_path):
    write_sources(tmp_path, "mock")
    tiny_region().to_csv(tmp_path / "region_monthly_rate.csv", index=False)
    pd.DataFrame({
        "month": [f"2025-{m:02d}" for m in range(1, 13)],
        "box": "box_3x3", "rate": 0.4, "units": "mm/hr",
    }).to_csv(tmp_path / "gpcp_box_monthly_rate.csv", index=False)
    aggregate.run(tmp_path, tmp_path)
    box = pd.read_csv(tmp_path / "annual_box.csv")
    assert "GPCP V3.3" in set(box["dataset"])
    annual_text = (tmp_path / "annual.json").read_text(encoding="utf-8")
    assert "GPCP" not in annual_text


def test_missing_input_fails_clearly(tmp_path):
    write_sources(tmp_path, "giovanni_csv")
    with pytest.raises(FileNotFoundError):
        aggregate.choose_input(tmp_path)