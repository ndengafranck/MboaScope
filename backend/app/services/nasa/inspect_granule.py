"""Spike: open ONE IMERG monthly granule and print its structure. Owner: Developer A (task A1).

CLI: python -m app.cli inspect-granule [--month 2024-12]

Confirms before the full fetch: the HDF5 group and variable names, dimension
order (time, lon, lat), the units attribute, the fill value, and that the
requested month is published. Prints the 3 x 3 cells around Douala.
"""
from __future__ import annotations

from app.core.config import DATASET, END_YEAR


def inspect(month: str = f"{END_YEAR}-12") -> None:
    import earthaccess
    import xarray as xr

    from app.services.nasa.fetch_imerg import login

    login()
    results = earthaccess.search_data(
        short_name=DATASET["short_name"], version=DATASET["version"], temporal=(f"{month}-01", f"{month}-28")
    )
    if not results:
        print(
            f"inspect: no {DATASET['short_name']} v{DATASET['version']} granule for {month}. "
            "V07 Final stops in 2025 (NASA is moving IMERG to V08); try an earlier month."
        )
        return
    print("inspect: granule", results[0].data_links()[0])
    handle = earthaccess.open(results[:1])[0]
    ds = xr.open_dataset(handle, group="Grid", engine="h5netcdf")
    print(ds)
    da = ds["precipitation"]
    print("dims:", da.dims, "units:", da.attrs.get("units"), "fill:", da.attrs.get("_FillValue"))
    print(da.sel(lat=slice(3.9, 4.2), lon=slice(9.6, 9.9)).squeeze().values)
