"""Tests for app/services/analytics/stats.py. Seeded, no network."""
import math

import numpy as np
import pytest

from app.services.analytics import stats

YEARS = np.arange(2001, 2026)  # n = 25


def test_known_slope_recovered_in_ci():
    rng = np.random.default_rng(42)
    hits = 0
    for _ in range(200):
        x = 3700 + 10 * (YEARS - YEARS[0]) + rng.normal(0, 300, YEARS.size)
        _, _, low, high = stats.sen_slope_ci(YEARS, x)
        hits += low <= 10 <= high
    assert hits >= 180, hits


def test_noise_false_positive_rate():
    rng = np.random.default_rng(7)
    fp = sum(stats.mk_original(rng.normal(3700, 300, 25))["p"] < 0.05 for _ in range(400))
    assert 0.01 <= fp / 400 <= 0.12, fp


def test_pettitt_finds_step():
    rng = np.random.default_rng(3)
    x = np.r_[rng.normal(3500, 100, 13), rng.normal(4200, 100, 12)]
    idx, k, p = stats.pettitt(x)
    assert abs(idx - 13) <= 1
    assert p < 0.05


def test_constant_series_no_crash():
    x = np.full(25, 3700.0)
    assert stats.mk_original(x)["trend"] == "no trend"
    assert stats.mk_hamed_rao(x)["trend"] == "no trend"
    assert stats.lag1_autocorr(x) == (0.0, False)
    slope, *_ = stats.sen_slope_ci(YEARS, x)
    assert slope == 0
    stats.pettitt(x)


def test_short_series_raises():
    for fn in (stats.lag1_autocorr, stats.mk_original, stats.mk_hamed_rao, stats.pettitt):
        with pytest.raises(ValueError):
            fn([1.0] * 9)
    with pytest.raises(ValueError):
        stats.sen_slope_ci(range(9), [1.0] * 9)


def test_hand_computed_mann_kendall():
    # pymannkendall needs n >= 10 in our wrapper, so we check the textbook
    # formulas on a 6-value series directly, then the wrapper on a 10-value one.
    x = [1, 3, 2, 5, 4, 6]
    n = len(x)
    s = sum(np.sign(x[j] - x[i]) for i in range(n) for j in range(i + 1, n))
    assert s == 11  # 15 pairs: 13 up, 2 down
    var = n * (n - 1) * (2 * n + 5) / 18
    assert var == pytest.approx(28.333, abs=1e-3)
    z = (s - 1) / math.sqrt(var)
    assert z == pytest.approx(1.8787, abs=1e-3)

    x10 = [1, 3, 2, 5, 4, 6, 8, 7, 10, 9]
    s10 = sum(np.sign(x10[j] - x10[i]) for i in range(10) for j in range(i + 1, 10))
    var10 = 10 * 9 * 25 / 18
    z10 = (s10 - 1) / math.sqrt(var10)
    p10 = 2 * (1 - 0.5 * (1 + math.erf(abs(z10) / math.sqrt(2))))
    r = stats.mk_original(x10)
    assert r["s"] == s10
    assert r["z"] == pytest.approx(z10, abs=1e-9)
    assert r["p"] == pytest.approx(p10, abs=1e-9)