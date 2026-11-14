"""Rate to monthly total conversion. Owner: Processing. Stub: implement per docs/prompts/processing.md, issue #13."""
from __future__ import annotations


def monthly_total_mm(rate: float, units: str | bytes, year: int, month: int) -> float:
    """Convert a monthly mean rate to a monthly total in mm.

    mm/hr, mm/h, mm hr-1, mm h-1: rate x 24 x days in month.
    mm/day, mm/d, mm d-1: rate x days in month.
    mm/month, mm: unchanged.
    Anything else raises ValueError naming the unit. Bytes are decoded; units are
    lowercased and stripped of spaces before matching. Days come from calendar.monthrange.
    """
    raise NotImplementedError("units.monthly_total_mm: see docs/prompts/processing.md #13")


def main() -> None:
    raise NotImplementedError("units has no CLI")


if __name__ == "__main__":
    main()
