"""Tests for app/services/gis (regions and spatial). Synthetic data, no network."""
import pandas as pd
import pytest

from app.models import database as db
from app.services.gis import spatial
from app.services.gis.regions import get_region, load_regions
from app.services.nasa.precipitation import add_mm, load_region_input

DOUALA = get_region("douala")
LATS = [3.95, 4.05, 4.15]
LONS = [9.65, 9.75, 9.85]


def tiny_region(year: int = 2025, drop_month: int | None = None) -> pd.DataFrame:
    """9 cells inside Douala's box_3x3 with rates 1 to 9 mm/hr for every month."""
    cells, rate = [], 1.0
    for lat in LATS:
        for lon in LONS:
            cells.append((lat, lon, rate))
            rate += 1
    rows = [
        {"month": f"{year}-{m:02d}", "lat": lat, "lon": lon, "rate": r, "units": "mm/hr"}
        for m in range(1, 13) if m != drop_month
        for lat, lon, r in cells
    ]
    return pd.DataFrame(rows)


# ------------------------------------------------------------ regions


def test_douala_boxes_match_the_original_study_design():
    assert DOUALA.box_bounds("box_1x1") == [4.0, 4.1, 9.7, 9.8]
    assert DOUALA.box_bounds("box_3x3") == [3.9, 4.2, 9.6, 9.9]
    assert DOUALA.box_bounds("box_5x5") == [3.8, 4.3, 9.5, 10.0]
    assert DOUALA.grid_bounds == [3.6, 4.5, 9.3, 10.2]


@pytest.mark.parametrize("region", list(load_regions().values()), ids=lambda r: r.id)
def test_every_region_centre_is_a_cell_centre_in_cameroon(region):
    for value in (region.centre_lat, region.centre_lon):
        assert round(value * 100) % 10 == 5, f"{region.id}: {value} is not an x.x5 cell centre"
    assert 1.6 < region.centre_lat < 13.1 and 8.4 < region.centre_lon < 16.2
    assert len(region.grid_cells()) == 81


def test_unknown_region_raises():
    from app.core.errors import RegionNotFound

    with pytest.raises(RegionNotFound):
        get_region("paris")


# ------------------------------------------------------------ extraction and annual totals


def test_exact_box_mean():
    annual = spatial.box_annual(add_mm(tiny_region()), DOUALA.box_bounds("box_3x3"))
    assert annual.loc[0, "total_mm"] == pytest.approx(5 * 24 * 365)  # mean rate 5 mm/hr
    assert bool(annual.loc[0, "complete"]) is True


def test_missing_month_excludes_year():
    annual = spatial.box_annual(add_mm(tiny_region(drop_month=7)), DOUALA.box_bounds("box_3x3"))
    assert int(annual.loc[0, "months_present"]) == 11
    assert bool(annual.loc[0, "complete"]) is False


def test_box_cell_counts_on_full_grid():
    grid = pd.DataFrame(DOUALA.grid_cells(), columns=["lat", "lon"])
    counts = {
        box: len(spatial.cells_in_box(grid, DOUALA.box_bounds(box))[["lat", "lon"]].drop_duplicates())
        for box in ("box_1x1", "box_3x3", "box_5x5")
    }
    assert counts == {"box_1x1": 1, "box_3x3": 9, "box_5x5": 25}


def test_wrong_box_raises():
    grid = pd.DataFrame({"lat": [3.95, 4.05], "lon": [9.65, 9.65]})
    with pytest.raises(ValueError):
        spatial.cells_in_box(grid, DOUALA.box_bounds("box_3x3"))


def test_implausible_year_is_flagged():
    annual = pd.DataFrame({"year": [2001, 2002], "total_mm": [3700.0, 40.0], "complete": [True, True]})
    assert spatial.implausible_years(annual) == [2002]


def test_annual_points_round_to_whole_mm():
    annual = spatial.box_annual(add_mm(tiny_region()), DOUALA.box_bounds("box_3x3"))
    assert spatial.annual_points(annual) == [{"year": 2025, "total_mm": 43800, "months_present": 12, "complete": True}]


# ------------------------------------------------------------ input switch (plan A / plan B)


def full_grid(rate: float = 5.0, year: int = 2025) -> pd.DataFrame:
    return pd.DataFrame([
        {"month": f"{year}-{m:02d}", "lat": lat, "lon": lon, "rate": rate, "units": "mm/hr"}
        for m in range(1, 13) for lat, lon in DOUALA.grid_cells()
    ])


def test_plan_a_region_input(tmp_db):
    db.replace_observations("douala", full_grid())
    db.upsert_source("douala", {"access_method": "mock", "source_units": "mm/hr",
                                "period": {"start": "2025-01", "end": "2025-12"}})
    ra = spatial.build_region_annual(DOUALA, load_region_input("douala"), 2025, 2025)
    assert ra.kind == "region"
    assert set(ra.boxes) == {"box_1x1", "box_3x3", "box_5x5"}
    assert all(f.loc[0, "total_mm"] == pytest.approx(43800) for f in ra.boxes.values())
    assert len(ra.cells) == 81


def test_partial_grid_fails_loudly(tmp_db):
    db.replace_observations("douala", tiny_region())  # only 9 cells: box_5x5 cannot be built
    db.upsert_source("douala", {"access_method": "mock", "source_units": "mm/hr",
                                "period": {"start": "2025-01", "end": "2025-12"}})
    with pytest.raises(ValueError, match="expected 25"):
        spatial.build_region_annual(DOUALA, load_region_input("douala"), 2025, 2025)


def test_plan_b_uses_box_rows_only(tmp_db):
    db.replace_observations("douala", tiny_region())  # must be ignored under plan B
    db.replace_box_observations("douala", [
        {"month": f"2025-{m:02d}", "box": "box_3x3", "rate": 0.5, "units": "mm/hr"} for m in range(1, 13)
    ])
    db.upsert_source("douala", {"access_method": "giovanni_csv", "source_units": "mm/hr",
                                "period": {"start": "2025-01", "end": "2025-12"}})
    ra = spatial.build_region_annual(DOUALA, load_region_input("douala"), 2025, 2025)
    assert list(ra.boxes) == ["box_3x3"]
    assert ra.boxes["box_3x3"].loc[0, "total_mm"] == pytest.approx(0.5 * 24 * 365)
    assert ra.cells is None


def test_region_without_data_fails_clearly(tmp_db):
    from app.core.errors import NoDataForRegion

    with pytest.raises(NoDataForRegion):
        load_region_input("douala")
