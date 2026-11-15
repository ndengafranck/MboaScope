"""Task A8: GPCP V3.3 as a sensitivity row. No network."""
import numpy as np
import xarray as xr
from fastapi.testclient import TestClient

from app.main import app
from app.models import database as db
from app.services.gis.regions import load_regions
from app.services.nasa import fetch_gpcp, mock


def make_gpcp_file(path, value=5.0):
    """A file shaped like GPCPMON V3.3: 0.5 degree, lat north to south, mm/day, fill -99999."""
    lat = np.arange(89.75, -90, -0.5, dtype="float32")
    lon = np.arange(-179.75, 180, 0.5, dtype="float32")
    data = np.full((1, lat.size, lon.size), value, dtype="float32")
    data[0, lat == 10.75, lon == 14.25] = -99999.0  # Maroua's cell is missing
    da = xr.DataArray(data, dims=("time", "lat", "lon"), coords={"lat": lat, "lon": lon},
                      attrs={"units": "mm/day"})
    ds = xr.Dataset({"sat_gauge_precip": da})
    ds["sat_gauge_precip"].encoding["_FillValue"] = -99999.0
    ds.to_netcdf(path, engine="h5netcdf")


def test_month_and_cell_centre():
    assert fetch_gpcp.month_of("GPCPMON_L3_200101_V3.3.nc4") == "2001-01"
    assert fetch_gpcp.cell_centre(4.05) == 4.25
    assert fetch_gpcp.cell_centre(9.75) == 9.75
    assert fetch_gpcp.cell_centre(10.55) == 10.75


def test_read_cell_rates_takes_the_cell_containing_the_centre(tmp_path):
    path = tmp_path / "GPCPMON_L3_202412_V3.3.nc4"
    make_gpcp_file(path)
    regions = list(load_regions().values())
    rates, units = fetch_gpcp.read_cell_rates(path, regions)
    assert units == "mm/day"
    assert rates["douala"] == 5.0
    assert rates["maroua"] is None  # fill value is dropped, never stored as rain


def test_replace_box_rows_keeps_other_boxes(tmp_db):
    db.replace_box_observations("douala", [{"month": "2001-01", "box": "box_3x3", "rate": 1.0, "units": "mm/hr"}])
    db.replace_box_rows("douala", fetch_gpcp.BOX, [{"month": "2001-01", "rate": 2.0, "units": "mm/day"}])
    boxes = set(db.read_box_observations("douala")["box"])
    assert boxes == {"box_3x3", fetch_gpcp.BOX}


def test_gpcp_row_appears_in_sensitivity_and_never_in_headline(tmp_db):
    mock.seed_all(["garoua"])
    rows = [{"month": f"{y}-{m:02d}", "rate": 2.0 + 0.01 * y - 20, "units": "mm/day"}
            for y in range(2001, 2025) for m in range(1, 13)]
    db.replace_box_rows("garoua", fetch_gpcp.BOX, rows)
    body = TestClient(app).post("/api/analysis/trends", json={"region_id": "garoua"}).json()
    gpcp = [r for r in body["sensitivity"] if r["box"] == fetch_gpcp.BOX]
    assert len(gpcp) == 1 and gpcp[0]["dataset"] == "GPCP V3.3" and gpcp[0]["n_years"] == 24
    assert body["headline"]["dataset"] == "IMERG V07" and body["headline"]["box"] == "box_3x3"


def test_no_gpcp_data_means_no_gpcp_row(tmp_db):
    mock.seed_all(["garoua"])
    body = TestClient(app).post("/api/analysis/trends", json={"region_id": "garoua"}).json()
    assert all(r["dataset"] == "IMERG V07" for r in body["sensitivity"])
