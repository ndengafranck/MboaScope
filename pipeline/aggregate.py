"""Annual CSVs and annual.json. CLI: python -m pipeline.aggregate. Owner: Processing (issue #14)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from pipeline import units
from pipeline.common import INTERIM, WEB_DATA, is_mock_run, read_sources, write_json
from pipeline.config import BOXES, DATASET

TOL = 1e-6
VALID_CELL_COUNTS = (1, 9, 25)
MIN_PLAUSIBLE_MM = 1000
MAX_PLAUSIBLE_MM = 8000
GPCP_LABEL = "GPCP V3.3"
BOX_COLUMNS = ["dataset", "box", "year", "total_mm", "months_present", "complete"]
CELL_COLUMNS = ["lat", "lon", "year", "total_mm", "complete"]


def choose_input(interim: Path = INTERIM) -> tuple[pd.DataFrame, str]:
    """Pick the input named by sources.json. Never decide by which file exists."""
    method = read_sources(interim / "sources.json")["access_method"]
    if method in ("mock", "earthaccess"):
        path, kind = interim / "region_monthly_rate.csv", "region"
    elif method == "giovanni_csv":
        path, kind = interim / "box_monthly_rate.csv", "box"
    else:
        raise ValueError(f"unknown access_method {method!r} in sources.json")
    if not path.exists():
        raise FileNotFoundError(f"{path} is missing (access_method={method})")
    print(f"aggregate: input = {path.name} (access_method={method})")
    return pd.read_csv(path), kind


def add_mm(df: pd.DataFrame) -> pd.DataFrame:
    """Add year and the monthly total in mm to every row."""
    df = df.copy()
    df["year"] = df["month"].str[:4].astype(int)
    month = df["month"].str[5:7].astype(int)
    df["mm"] = [
        units.monthly_total_mm(r, u, y, m)
        for r, u, y, m in zip(df["rate"], df["units"], df["year"], month)
    ]
    return df


def cells_in_box(df: pd.DataFrame, bounds: list[float]) -> pd.DataFrame:
    """Rows whose cell centre falls inside [south, north, west, east]."""
    south, north, west, east = bounds
    mask = (
        (df["lat"] > south - TOL) & (df["lat"] < north + TOL)
        & (df["lon"] > west - TOL) & (df["lon"] < east + TOL)
    )
    sub = df[mask]
    n_cells = len(sub[["lat", "lon"]].drop_duplicates())
    if n_cells not in VALID_CELL_COUNTS:
        raise ValueError(f"box {bounds} contains {n_cells} cells, expected 1, 9 or 25")
    return sub


def to_annual(monthly: pd.DataFrame) -> pd.DataFrame:
    """One row per month (year, mm) to one row per year. No gap filling."""
    out = (
        monthly.groupby("year")["mm"]
        .agg(total_mm="sum", months_present="count")
        .reset_index()
        .sort_values("year")
    )
    out["complete"] = out["months_present"] == 12
    return out.reset_index(drop=True)


def box_annual(df_mm: pd.DataFrame, bounds: list[float]) -> pd.DataFrame:
    """Box monthly value = plain mean of its cells, then summed per year."""
    sub = cells_in_box(df_mm, bounds)
    monthly = sub.groupby(["month", "year"], as_index=False)["mm"].mean()
    return to_annual(monthly)


def box_rows(annual: pd.DataFrame, box: str, dataset: str) -> list[dict]:
    """Rows for annual_box.csv. total_mm stays unrounded; complete is lowercase text."""
    return [
        {
            "dataset": dataset,
            "box": box,
            "year": int(r.year),
            "total_mm": float(r.total_mm),
            "months_present": int(r.months_present),
            "complete": "true" if r.complete else "false",
        }
        for r in annual.itertuples()
    ]


def box_json(annual: pd.DataFrame, box: str) -> dict:
    """One box entry for annual.json, millimetres rounded to 0 decimals."""
    return {
        "label": BOXES[box]["label"],
        "bounds": BOXES[box]["bounds"],
        "years": [
            {
                "year": int(r.year),
                "total_mm": int(round(r.total_mm)),
                "months_present": int(r.months_present),
                "complete": bool(r.complete),
            }
            for r in annual.itertuples()
        ],
        "excluded_years": [int(y) for y in annual.loc[~annual["complete"], "year"]],
    }


def warn_implausible(annual: pd.DataFrame, label: str) -> None:
    """Loud warning for complete years outside 1,000 to 8,000 mm (usually a unit error)."""
    bad = annual[
        annual["complete"]
        & ((annual["total_mm"] < MIN_PLAUSIBLE_MM) | (annual["total_mm"] > MAX_PLAUSIBLE_MM))
    ]
    if len(bad):
        print(f"WARNING {label}: implausible annual totals in {bad['year'].tolist()}, check units")


def cell_annual(df_mm: pd.DataFrame) -> pd.DataFrame:
    """Per-cell annual totals for the region (annual_cell.csv)."""
    cells = (
        df_mm.groupby(["lat", "lon", "year"])["mm"]
        .agg(total_mm="sum", months_present="count")
        .reset_index()
    )
    cells["complete"] = (cells["months_present"] == 12).map({True: "true", False: "false"})
    return cells[CELL_COLUMNS]


def run(interim: Path = INTERIM, web_data: Path = WEB_DATA) -> None:
    raw, kind = choose_input(interim)
    df = add_mm(raw)

    if kind == "region":
        frames = {box: box_annual(df, cfg["bounds"]) for box, cfg in BOXES.items()}
    else:
        monthly = df[df["box"] == "box_3x3"][["month", "year", "mm"]]
        frames = {"box_3x3": to_annual(monthly)}

    rows: list[dict] = []
    boxes_json: dict[str, dict] = {}
    for box, annual in frames.items():
        warn_implausible(annual, box)
        rows += box_rows(annual, box, DATASET["label"])
        boxes_json[box] = box_json(annual, box)

    gpcp_path = interim / "gpcp_box_monthly_rate.csv"
    if gpcp_path.exists():
        gpcp = add_mm(pd.read_csv(gpcp_path))
        gpcp_annual = to_annual(gpcp[gpcp["box"] == "box_3x3"][["month", "year", "mm"]])
        warn_implausible(gpcp_annual, "GPCP box_3x3")
        rows += box_rows(gpcp_annual, "box_3x3", GPCP_LABEL)
        print("aggregate: GPCP V3.3 rows added to annual_box.csv")

    pd.DataFrame(rows, columns=BOX_COLUMNS).to_csv(interim / "annual_box.csv", index=False)

    cell_path = interim / "annual_cell.csv"
    if kind == "region":
        cell_annual(df).to_csv(cell_path, index=False)
    elif cell_path.exists():
        cell_path.unlink()  # a stale plan A file must not feed the trend map under plan B

    write_json(web_data / "annual.json", {"boxes": boxes_json}, is_mock_run(interim / "sources.json"))
    print(f"aggregate: wrote annual_box.csv ({len(rows)} rows), annual.json ({', '.join(boxes_json)})")


def main() -> None:
    run()


if __name__ == "__main__":
    main()