"""Parse a Giovanni area-averaged CSV (plan B). Owner: Developer A.

CLI: python -m app.cli import-giovanni FILE --region douala [--units U] [--activate]

Always stores the box_3x3 monthly rates for the region in box_observations,
values exactly as Giovanni gives them. Switches the region to plan B (sources
row access_method = giovanni_csv) only with --activate; without it the rows are
kept for the one-month cross-check against the per-cell data.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

from app.models import database as db

BOX = "box_3x3"
BOX_COLUMNS = ["month", "box", "rate", "units"]
UNITS_PATTERN = re.compile(r"\b(mm\s*/\s*(?:hr|h|day|d|month)|mm\s+(?:hr|h|d)-1)\b", re.IGNORECASE)
FILL_PATTERN = re.compile(r"^fill value", re.IGNORECASE)


def parse(text: str, units: str | None = None) -> tuple[list[dict], str]:
    """Return (rows, units) from the text of a Giovanni area-averaged time series CSV.

    Skips metadata lines until the header row whose first cell is `time`. Units come
    from the metadata lines, else from `units`. Fill values are dropped (the month is
    then missing, never filled).
    """
    found_units: str | None = None
    fill_values: set[float] = set()
    rows: list[dict] = []
    in_data = False

    for record in csv.reader(text.splitlines()):
        cells = [c.strip() for c in record]
        if not cells or not any(cells):
            continue
        if not in_data:
            if cells[0].lower() == "time":
                in_data = True
                continue
            line = ",".join(cells)
            if found_units is None:
                match = UNITS_PATTERN.search(line)
                if match:
                    found_units = re.sub(r"\s+", "", match.group(1)).lower()
            if FILL_PATTERN.match(cells[0]) and len(cells) > 1:
                try:
                    fill_values.add(float(cells[1]))
                except ValueError:
                    pass
            continue
        if len(cells) < 2 or not re.match(r"^\d{4}-\d{2}", cells[0]):
            continue
        try:
            value = float(cells[1])
        except ValueError:
            continue
        if value in fill_values or value < -9000:
            continue
        rows.append({"month": cells[0][:7], "rate": value})

    if not in_data:
        raise ValueError("no header row starting with 'time' found: is this a Giovanni time series CSV?")
    if not rows:
        raise ValueError("the Giovanni file has a header but no data rows")
    final_units = found_units or (units.strip() if units else None)
    if not final_units:
        raise ValueError("units not found in the file's metadata: pass --units (for example --units mm/hr)")

    by_month = {r["month"]: r["rate"] for r in rows}
    out = [{"month": m, "box": BOX, "rate": by_month[m], "units": final_units} for m in sorted(by_month)]
    return out, final_units




def sources_payload(rows: list[dict], units: str, source_file: Path) -> dict:
    return {
        "access_method": "giovanni_csv",
        "source_units": units,
        "period": {"start": rows[0]["month"], "end": rows[-1]["month"]},
        "granule_count": 0,
        "notes": [
            "area average computed by Giovanni",
            f"source file: {Path(source_file).name}",
            "box_3x3 only: no per-cell values, so the trend map and box sensitivity are not available",
        ],
    }


def run(
    file: Path,
    region_id: str,
    units: str | None = None,
    activate: bool = False,
    db_path: Path | None = None,
) -> list[dict]:
    rows, final_units = parse(Path(file).read_text(encoding="utf-8-sig"), units)
    db.replace_box_observations(region_id, rows, db_path)
    print(f"giovanni: stored {len(rows)} months for {region_id} ({rows[0]['month']} to {rows[-1]['month']}, {final_units})")
    if activate:
        db.upsert_source(region_id, sources_payload(rows, final_units, Path(file)), db_path)
        print(f"giovanni: {region_id} now uses access_method giovanni_csv (plan B active)")
    else:
        print("giovanni: sources unchanged (cross-check only; add --activate for plan B)")
    return rows
