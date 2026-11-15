"""Tests for pipeline/units.py (issue #13)."""
import pytest

from pipeline.units import monthly_total_mm


@pytest.mark.parametrize(
    "year, month, expected",
    [(2024, 2, 696), (2025, 2, 672), (2025, 7, 744), (2025, 6, 720)],
)
def test_one_mm_per_hour(year, month, expected):
    assert monthly_total_mm(1.0, "mm/hr", year, month) == pytest.approx(expected)


@pytest.mark.parametrize("spelling", ["mm/hr", "mm/h", "mm hr-1", "mm h-1", " MM/HR "])
def test_hourly_spellings(spelling):
    assert monthly_total_mm(1.0, spelling, 2025, 1) == pytest.approx(744)


def test_daily_path():
    assert monthly_total_mm(2.0, "mm/day", 2025, 6) == pytest.approx(60)
    assert monthly_total_mm(2.0, "mm d-1", 2025, 6) == pytest.approx(60)


def test_monthly_path_unchanged():
    assert monthly_total_mm(310.5, "mm/month", 2025, 3) == pytest.approx(310.5)


def test_bytes_input():
    assert monthly_total_mm(1.0, b"mm/hr", 2025, 1) == pytest.approx(744)


def test_unknown_unit_raises():
    with pytest.raises(ValueError, match="inches"):
        monthly_total_mm(1.0, "inches", 2025, 1)