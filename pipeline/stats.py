"""Pure statistics, no file I/O. Owner: Analytics. Stub: implement per docs/prompts/analytics.md, issue #16."""
from __future__ import annotations

from typing import Sequence


def lag1_autocorr(x: Sequence[float]) -> tuple[float, bool]:
    """Lag-1 autocorrelation and whether |r1| > 1.96 / sqrt(n)."""
    raise NotImplementedError


def mk_original(x: Sequence[float]) -> dict:
    """pymannkendall.original_test: tau, z, p, trend, S."""
    raise NotImplementedError


def mk_hamed_rao(x: Sequence[float]) -> dict:
    """pymannkendall.hamed_rao_modification_test: z, p, trend."""
    raise NotImplementedError


def sen_slope_ci(years: Sequence[int], x: Sequence[float]) -> tuple[float, float, float, float]:
    """scipy.stats.theilslopes(x, years, alpha=0.95): (slope, intercept, low, high).

    The intercept is the line value at year 0; analyse.py converts it for the contract.
    """
    raise NotImplementedError


def pettitt(x: Sequence[float]) -> tuple[int, float, float]:
    """Pettitt test: (change_index, k, p). Change index is the first index of the new regime.

    U_t = sum over i <= t, j > t of sign(x_j - x_i); K = max |U_t|;
    p = 2 exp(-6 K^2 / (n^3 + n^2)), capped at 1. Raises ValueError for fewer than 10 values.
    """
    raise NotImplementedError


def main() -> None:
    raise NotImplementedError("stats has no CLI")


if __name__ == "__main__":
    main()
