# Science: what MboaScope may and may not claim

## Question

Does the NASA satellite record show a statistically detectable monotonic trend in annual rainfall over the Douala area, 2001-2025, and how confident can we be?

## Data

- **Primary:** GPM IMERG Final, monthly, Version 07 (`GPM_3IMERGM`), DOI 10.5067/GPM/IMERG/3B-MONTH/07. Grid 0.1 degree (about 11 km). Available from June 2000, about 4 months behind real time.
- The file stores a **mean precipitation rate** (check the `units` attribute; usually mm/hr), not a monthly total.
- **Optional cross-check:** GPCP monthly V3.3 (0.5 degree, different satellite inputs).
- **Never use** TRMM 3B43 (discontinued 31 Dec 2019) and never join two products into one series.

## Study area (edges on 0.1 degree cell edges; south, north, west, east)

| ID | Bounds | Size | Role |
| --- | --- | --- | --- |
| `box_1x1` | 4.0, 4.1, 9.7, 9.8 | about 11 km | sensitivity |
| `box_3x3` | 3.9, 4.2, 9.6, 9.9 | about 33 km | **headline** |
| `box_5x5` | 3.8, 4.3, 9.5, 10.0 | about 55 km | sensitivity |
| `region` | 3.6, 4.5, 9.3, 10.2 | 9 x 9 cells | exploratory trend map |

The Processing owner confirms on a map that the 3x3 box covers the city and is mostly land. Only they change `pipeline/config.py`.

## Processing rules

- Monthly total (mm) = rate (mm/hr) x 24 x days in that month (leap years counted). Other units handled explicitly; unknown units raise an error.
- Box value = plain mean of the cells whose centres fall inside the box.
- Annual total = sum of 12 monthly totals. A year with fewer than 12 months is excluded and listed. No gap filling.

## Statistics (headline pre-registered: IMERG, `box_3x3`, 2001-2025, alpha 0.05)

- Lag-1 autocorrelation; significant if |r1| > 1.96 / sqrt(n).
- Mann-Kendall original test always reported; Hamed-Rao modified test is the primary test when lag-1 autocorrelation is significant.
- Sen's slope (mm per year) with 95% confidence interval, always reported whatever the p-value.
- Relative change: slope x 10 / mean annual total x 100, in % per decade.
- Pettitt change-point test, to separate a step from a gradual trend.
- Sensitivity runs (other boxes, GPCP) are robustness checks. They are never promoted to the headline.
- Trend map: per-cell tests are exploratory; always show the expected number of false positives (alpha x number of cells).

## Known threats the app must show, not hide

1. **Satellite change in 2014.** IMERG is calibrated to TRMM until May 2014 and to GPM from June 2014. NASA warns the changing satellite constellation can create artifacts in multi-year studies. A step in 2014 can look like a trend.
2. **Coastal location.** NASA states lower IMERG skill over coastal zones; Douala sits on the Wouri estuary.
3. **Short record.** 25 annual values give low statistical power. A non-significant result is a valid, expected outcome.
4. **Area estimate.** A grid average is a satellite estimate over an area, not a station measurement.

## Allowed and banned wording

| Allowed | Banned |
| --- | --- |
| "The satellite record shows a statistically significant increase / decrease" | "proves", "confirms climate change", any cause (climate change, deforestation, urbanisation, humans) |
| "No statistically significant trend was detected" | "Rainfall did not change", "rainfall is stable" |
| "Satellite estimate averaged over a 33 km box around Douala" | "Measured in Douala", "station data", "rain gauge" |
| "The estimated change is X mm per year (95% CI A to B)" | "Rainfall will increase / decrease", any forecast |
| "The change coincides with the 2014 satellite transition and may be an artifact" | Hiding or softening the 2014 caveat |
