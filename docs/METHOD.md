# Method

How MboaScope gets from satellite files to the sentence on the screen. Written for a first-year student. The numbers themselves are on the main page; this page explains where they come from.

## 1. The question

Does the NASA satellite record show a steady upward or downward trend in yearly rainfall over Douala from 2001 to 2025, and how sure can we be?

We fixed the main test before looking at the data: one dataset, one box, one period, one significance level (0.05). Everything else is a robustness check.

## 2. The data

- **Product:** GPM IMERG Final Precipitation, monthly, Version 07 (`GPM_3IMERGM`), from NASA GES DISC. DOI: [10.5067/GPM/IMERG/3B-MONTH/07](https://doi.org/10.5067/GPM/IMERG/3B-MONTH/07).
- IMERG combines readings from many satellites into one rainfall estimate on a grid of 0.1 degree cells (about 11 km wide).
- We use one product only. We never join two products into one series, because a jump at the join would look like a trend.
- Optional cross-check: GPCP monthly V3.3, a coarser product built from different inputs. It is shown as a check, never as the main result.

## 3. The boxes

The grid cells are averaged inside square boxes around Douala:

| Box | Size | Role |
| --- | --- | --- |
| 3 x 3 cells | about 33 km | main result |
| 1 x 1 cell | about 11 km | check: does a smaller area agree? |
| 5 x 5 cells | about 55 km | check: does a larger area agree? |
| 9 x 9 cells | about 100 km | exploratory map, one test per cell |

A box value is the plain average of the cells whose centres fall inside it.

## 4. From rate to yearly total

The monthly file does not store a monthly total. It stores an average **rate**, usually in millimetres per hour. So for each month:

monthly total (mm) = rate (mm per hour) x 24 hours x number of days in that month

February has 29 days in leap years. Other units are converted explicitly, and an unknown unit stops the program with an error.

The yearly total is the sum of the 12 monthly totals. A year with a missing month is left out and listed on the page. We never fill gaps.

## 5. The tests, and why each one

- **Mann-Kendall test.** Asks whether later years tend to be higher (or lower) than earlier years. It looks only at the order of the values, not their size, so one very wet year cannot dominate it, and it does not assume the values follow a bell curve.
- **Lag-1 autocorrelation check.** If one year's total is linked to the next year's, the plain Mann-Kendall test becomes too confident. When that link is significant, we use the **modified Mann-Kendall test (Hamed-Rao)**, which corrects for it. Both results are kept in the data file.
- **Sen's slope.** The size of the change in millimetres per year: the median of the slopes between every pair of years. It comes with a 95% confidence interval and is always shown, significant or not. We also show it as a percentage of the average yearly total per decade.
- **Pettitt test.** Looks for a single year where the series jumps from one level to another. This matters because a one-time step (for example from a change in satellites) can look like a gradual trend.
- **Significance level 0.05.** A result is called significant when the chance of seeing such a pattern by luck alone, with no real trend, is below 5%.
- **Trend map** (when the full grid was downloaded). Each of the 81 cells is tested on its own. With 81 tests at 0.05, about 4 cells are expected to look significant by chance alone, so the map is exploratory and always shows that expected number.

## 6. The four limitations

1. **Satellite change in 2014.** IMERG is calibrated against the TRMM satellite until May 2014 and against GPM after that. NASA warns that such changes can create artifacts in multi-year studies. A step near 2014 may come from the data, not the weather.
2. **Coast.** NASA reports lower IMERG accuracy near coasts, and Douala sits on the Wouri estuary.
3. **Short record.** 25 yearly values give the tests little power. A small real change can go undetected, so "no significant trend" is a common and valid outcome. It does not mean rainfall stayed the same.
4. **Area estimate.** Every value is a satellite estimate averaged over a box, not a reading taken at one point on the ground.

The results describe the past record only. They do not explain why rainfall behaves as it does, and they say nothing about future years.

## 7. What the AI does and does not do

- **It does:** turn numbers that the analysis already produced into plain sentences. A fixed template (written in code) always produces a correct text. Optionally, Google Gemini rewrites three of the paragraphs to read more easily. The first sentence, with the verdict, the slope and its interval, is never rewritten.
- **It does not:** compute, choose or interpret anything. It never sees the raw data and never decides the verdict.
- **Every text is checked by code before it is shown:**
  - every number must already exist in the analysis file;
  - banned claims are rejected (causes, "proves", forecasts, "rainfall is stable", calling the data a local reading, and similar);
  - the wording must match the direction of the result.
  If a Gemini rewrite fails any check, the template text is shown instead. The data file records which one you see (`source`) and whether all checks passed.

## 8. Reproduce it

The code, the data contract and the tests are in the repository. `make build` reruns the whole chain; the README lists the plain commands for systems without `make`.
