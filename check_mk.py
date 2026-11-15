import math 
import numpy as np
import pandas as pd
from pipeline import stats

df = pd.read_csv("data/interim/annual_box.csv")
df = df[(df["box"] == "box_3x3") & (df["dataset"] == "IMERG V07")
        & (df["complete"].astype(str).str.lower() == "true")].sort_values("year")
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
print(f"library : S={lib['S']:.0f} z={lib['z']:.4f} p={lib['p']:.4f}")
print("MATCH" if abs(z - lib["z"]) < 1e-9 and abs(p - lib["p"]) < 1e-9 else "DIFFERENT")