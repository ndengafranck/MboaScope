"""Rate to monthly total conversion. Owner: Developer A."""
from __future__ import annotations

import calendar

HOURLY = {"mm/hr", "mm/h", "mmhr-1", "mmh-1"}
DAILY = {"mm/day", "mm/d", "mmd-1"}
MONTHLY = {"mm/month", "mm"}


def monthly_total_mm(rate: float, units: str | bytes, year: int, month: int) -> float:
    """Convert a monthly mean rate to a monthly total in mm.

    mm/hr, mm/h, mm hr-1, mm h-1: rate x 24 x days in month.
    mm/day, mm/d, mm d-1: rate x days in month.
    mm/month, mm: unchanged.
    Anything else raises ValueError naming the unit. Bytes are decoded; units are
    lowercased and stripped of spaces before matching. Days come from calendar.monthrange.
    """
    if isinstance(units, bytes):
        units = units.decode("utf-8")
    u = str(units).lower().replace(" ", "")
    days = calendar.monthrange(int(year), int(month))[1]
    if u in HOURLY:
        return float(rate) * 24 * days
    if u in DAILY:
        return float(rate) * days
    if u in MONTHLY:
        return float(rate)
    raise ValueError(f"unknown precipitation unit: {units!r}")


def main() -> None:
    raise NotImplementedError("units has no CLI")


if __name__ == "__main__":
    main()