"""Second implementation of Mann-Kendall, by hand, to validate stats.py (task A6).

Run from backend/: python scripts/check_mann_kendall.py [region_id]
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.config import HEADLINE_BOX  # noqa: E402
from app.services import investigation  # noqa: E402
from app.services.analytics import stats  # noqa: E402
from app.services.analytics.trends import complete_only  # noqa: E402

region_id = sys.argv[1] if len(sys.argv) > 1 else "douala"
df = complete_only(investigation.run(region_id).annual.boxes[HEADLINE_BOX])
x = df["total_mm"].to_numpy()
n = len(x)

# 1. S by hand: every pair (i, j) with i < j
S = sum(np.sign(x[j] - x[i]) for i in range(n) for j in range(i + 1, n))

# 2. Variance (no ties: real rainfall totals never tie exactly)
var = n * (n - 1) * (2 * n + 5) / 18

# 3. Z with the continuity correction
if S > 0:
    z = (S - 1) / math.sqrt(var)
elif S < 0:
    z = (S + 1) / math.sqrt(var)
else: 
    z = 0.0
    
# 4. Two-sided p from the normal distribution
p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))

lib = stats.mk_original(x)
print(f"by hand : S={S:.0f} var={var:.2f} z={z:.4f} p={p:.4f}")
print(f"library : S={lib['s']:.0f} z={lib['z']:.4f} p={lib['p']:.4f}")
print("MATCH" if abs(z - lib["z"]) < 1e-9 and abs(p - lib["p"]) < 1e-9 else "DIFFERENT")