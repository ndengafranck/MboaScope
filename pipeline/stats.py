"""Pure statistics, no file I/O. Owner: Analytics. Stub: implement per docs/prompts/analytics.md, issue #16."""
from __future__ import annotations

import math

import numpy as np
import pymannkendall as mk
from scipy import stats as sps

from typing import Sequence

MIN_N = 10

# Sequence[] means it accepts a list, tuple or a pandas column.
def _as_array(x: Sequence[float]) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    if arr.ndim != 1:
        raise ValueError("Expected a 1-D series")
    if np.isnan(arr).any():
        raise ValueError("series contains NaN; incomplete years must be dropped first")
    if arr.size < MIN_N:
        raise ValueError(f"need at least {MIN_N} values, got {arr.size}")
    
    return arr
    


def lag1_autocorr(x: Sequence[float]) -> tuple[float, bool]:
    arr = _as_array(x)
    if np.ptp(arr) == 0 :
        return 0.0, False
    d = arr - np.mean(arr)
    r1 = np.sum(d[:-1] * d[1:]) / np.sum(d ** 2)
    significant = abs(r1) > 1.96 / np.sqrt(arr.size)
    return float(r1), bool(significant)


def mk_original(x: Sequence[float]) -> dict:
    arr = _as_array(x)
    if np.ptp(arr) == 0:
        return {"tau": 0.0, "z": 0.0, "p": 1.0, "trend": "no trend", "s": 0.0}
    r = mk.original_test(arr)
    return {"tau": float(r.Tau), "z": float(r.z), "p": float(r.p), "trend": r.trend, "s": float(r.s)}


def mk_hamed_rao(x: Sequence[float]) -> dict:
    arr = _as_array(x)
    if np.ptp(arr) == 0:
        return {"z": 0.0, "p": 1.0, "trend": "no trend"}
    r = mk.original_test(arr)
    return {"z": float(r.z), "p": float(r.p), "trend": r.trend}

def sen_slope_ci(years: Sequence[int], x: Sequence[float]) -> tuple[float, float, float, float]:
    arr = _as_array(x)
    years = np.asarray(years, dtype=float)
    if years.shape != arr.shape:
        raise ValueError("years and x must have the same shape")
    slope, intercept, low, high = sps.theilslopes(arr, years, alpha=0.95)
    return float(slope), float(intercept), float(low), float(high)


def pettitt(x: Sequence[float]) -> tuple[int, float, float]:
    """Pettitt change-point test.

    Returns (change_index, K, p). change_index is the first index of the
    new regime (argmax |U_t| + 1). p = 2 exp(-6 K^2 / (n^3 + n^2)), capped at 1.
    """
    arr = _as_array(x)
    n = arr.size
    sign = np.sign(arr[None, :] - arr[:, None])  # sign[i, j] = sign(x_j - x_i)
    u = np.array([sign[: t + 1, t + 1 :].sum() for t in range(n - 1)])
    t_star = int(np.argmax(np.abs(u)))
    k = float(abs(u[t_star]))
    p = min(1.0, 2.0 * math.exp(-6.0 * k * k / (n ** 3 + n ** 2)))
    return t_star + 1, k, p


def main() -> None:
    raise NotImplementedError("stats has no CLI")


if __name__ == "__main__":
    main()
