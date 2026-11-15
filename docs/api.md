# Data contract v1.0

Modules communicate only through these files. Owner = the only role that writes the file. A change needs an issue labelled `contract` and Lead approval.

## Flow

```
Data ──> data/interim/region_monthly_rate.csv ─┐
     └─> data/interim/box_monthly_rate.csv  ───┤ (plan B only)
     └─> data/interim/sources.json             │
                                               v
Processing ──> data/interim/annual_box.csv, annual_cell.csv, web/public/data/annual.json
                                               v
Analytics  ──> web/public/data/analysis.json, spatial.json
                                               v
AI         ──> web/public/data/explanation.json
Lead       ──> web/public/data/provenance.json (pipeline/build.py runs everything in order)
Frontend   <── reads the five JSON files in web/public/data/
```

## Interim files (CSV, UTF-8, comma, header row, committed if under 5 MB)

### `data/interim/region_monthly_rate.csv` (owner: Data)
| column | type | example | rule |
| --- | --- | --- | --- |
| `month` | string `YYYY-MM` | `2001-01` | 2001-01 to END_YEAR-12 |
| `lat` | float, 2 decimals | `4.05` | cell centre |
| `lon` | float, 2 decimals | `9.75` | cell centre |
| `rate` | float | `0.153` | value as stored in the file, no conversion |
| `units` | string | `mm/hr` | exactly the file's `units` attribute |

### `data/interim/box_monthly_rate.csv` (owner: Data, plan B only)
Columns `month, box, rate, units`; `box` is always `box_3x3`.

### `data/interim/sources.json` (owner: Data)
```json
{"access_method": "earthaccess | giovanni_csv | mock",
 "source_units": "mm/hr",
 "period": {"start": "2001-01", "end": "2025-12"},
 "granules": [{"id": "3B-MO.MS.MRG.3IMERG.20010101-...V07B.HDF5", "month": "2001-01"}],
 "notes": ["..."]}
```
`access_method` is the single switch for the run. `mock` and `earthaccess` mean the region file is the input; `giovanni_csv` means the box file is the input (plan B). Nothing else decides this: a leftover file on disk is ignored. `pipeline/import_giovanni.py` writes `sources.json` only when called with `--activate` (`make giovanni FILE=... ACTIVATE=1`). Without it, it writes the box file only, for the cross-check.

### `data/interim/gpcp_box_monthly_rate.csv` (owner: Data, optional "should")
Columns `month, box, rate, units`; `box` is `box_3x3`; values are GPCP V3.3 box means as stored (no conversion).

### `data/interim/annual_box.csv` (owner: Processing)
Columns `dataset, box, year, total_mm, months_present, complete`. `dataset` is `IMERG V07` or `GPCP V3.3`; `complete` is the lowercase string `true` or `false` (pandas writes `True`/`False` by default: map the column before writing, and compare case-insensitively when reading). `total_mm` is unrounded here; rounding happens only in the web files.

### `data/interim/annual_cell.csv` (owner: Processing, only when the region file is the input)
Columns `lat, lon, year, total_mm, complete`. Same `complete` rule.

## Web files (`web/public/data/`, JSON)

Every file has `"contract_version": "1.0"`, `"generated_at"` (ISO 8601 UTC), `"is_mock"` (boolean). Display rounding is done by the producer: millimetres 0 decimals, slopes 1 decimal, p-values 3 decimals, percentages 1 decimal, correlations 2 decimals.

### `annual.json` (owner: Processing)
```json
{"contract_version":"1.0","generated_at":"2026-11-14T15:00:00Z","is_mock":true,
 "boxes":{"box_3x3":{"label":"Douala box, 3 x 3 cells (about 33 km)","bounds":[3.9,4.2,9.6,9.9],
   "years":[{"year":2001,"total_mm":3812,"months_present":12,"complete":true}],
   "excluded_years":[]}}}
```
`boxes` contains every box that could be computed (only `box_3x3` under plan B). IMERG only: GPCP rows stay in `annual_box.csv` and never appear here. `bounds` order is `[south, north, west, east]`, as in `docs/SCIENCE.md`.

### `analysis.json` (owner: Analytics)
```json
{"contract_version":"1.0","generated_at":"...","is_mock":true,
 "headline":{"box":"box_3x3","dataset":"IMERG V07","period":"2001-2025","n_years":25,"alpha":0.05,
   "mean_annual_mm":3700,"lag1_autocorr":0.12,"autocorr_significant":false,
   "mk_test_used":"original | hamed_rao",
   "mk_original":{"tau":0.08,"z":0.54,"p":0.589,"trend":"increasing | decreasing | no trend"},
   "mk_hamed_rao":{"z":0.51,"p":0.610,"trend":"no trend"},
   "sen_slope_mm_per_year":4.2,"sen_intercept_mm":3650,"sen_ci95":[-11.3,19.8],"pct_per_decade":1.1,
   "pettitt":{"change_year":2014,"k":64,"p":0.210,"significant":false},
   "verdict":"no_significant_trend | significant_increase | significant_decrease",
   "caveats":["sensor_change_2014","coastal_skill","short_record","area_estimate"]},
 "sensitivity":[{"box":"box_1x1","dataset":"IMERG V07","n_years":25,"p":0.500,
   "sen_slope_mm_per_year":3.9,"sen_ci95":[-15.0,22.1],"verdict":"no_significant_trend"}]}
```
`pettitt.change_year` is the first year of the new regime.

`sen_intercept_mm` (headline only) is the value of the Sen line at the first year of the period: median of the totals minus slope x (median of the years minus the first year), rounded to 0 decimals. The chart draws `sen_intercept_mm + sen_slope_mm_per_year x (year - first year)`. Frontend never computes a median.

### `spatial.json` (owner: Analytics)
```json
{"contract_version":"1.0","generated_at":"...","is_mock":true,"exploratory":true,
 "available":true,"n_cells":81,"alpha":0.05,"expected_false_positives":4.05,"n_significant":3,
 "cells":[{"lat":4.05,"lon":9.75,"mean_annual_mm":3700,"sen_slope_mm_per_year":4.2,"p":0.589}]}
```
Under plan B: `"available": false`, `"cells": []`.

### `explanation.json` (owner: AI)
```json
{"contract_version":"1.0","generated_at":"...","is_mock":true,
 "source":"template | gemini","model":null,"checks_passed":true,
 "summary":"...","what_it_means":"...","what_it_does_not_mean":"...",
 "limitations":["...","...","...","..."]}
```

### `provenance.json` (owner: Lead, written by `pipeline/build.py` from `sources.json`)
```json
{"contract_version":"1.0","generated_at":"...","is_mock":true,
 "dataset":{"name":"GPM IMERG Final Precipitation L3 1 month 0.1 degree x 0.1 degree V07",
   "short_name":"GPM_3IMERGM","version":"07","doi":"10.5067/GPM/IMERG/3B-MONTH/07",
   "variable":"precipitation","source_units":"mm/hr"},
 "access_method":"mock","period":{"start":"2001-01","end":"2025-12"},
 "granule_count":300,"code_commit":"abc1234","notes":["..."]}
```

## Python entry points (one command per module)

| Command | Owner | Reads | Writes |
| --- | --- | --- | --- |
| `make mock` | Data | nothing | region file + sources.json (`access_method: mock`) |
| `make spike` / `make fetch` | Data | Earthdata | region file + sources.json |
| `make giovanni FILE=path.csv` (add `ACTIVATE=1` to switch the run to plan B) | Data | Giovanni CSV | box file; sources.json only with `ACTIVATE=1` |
| `make process` | Processing | the input named by sources.json | annual_box.csv, annual_cell.csv, annual.json |
| `make analyse` | Analytics | annual CSVs | analysis.json, spatial.json |
| `make explain` (add `LLM=1` for Gemini) | AI | analysis.json | explanation.json |
| `make build` | Lead | everything | runs process, analyse, explain, writes provenance.json, validates all JSON |

`is_mock` propagates: if `sources.json` says `mock`, every downstream JSON says `is_mock: true`.

Without `make` (Windows): every target wraps one command, so `python -m pipeline.make_mock`, `python -m pipeline.aggregate`, `python -m pipeline.analyse`, `python -m pipeline.explain`, `python -m pipeline.build` and `python -m pytest -q` do the same on any system. The README lists them all.

## Who commits generated files

- Data commits its own interim files (region or box CSV, `sources.json`, the Giovanni download).
- Everyone else commits code and tests only. The annual CSVs and the five web JSON files are regenerated and committed by the Lead, with `make build`, after each pipeline merge (branch `feature/lead-4-build-<n>`). Each run stamps a new `generated_at`, so two people committing these files would conflict on every rebase.
- One exception: a Gemini rewrite. The AI owner commits `explanation.json` with `source: "gemini"`. A later `make build` without `LLM=1` keeps that file if every check still passes against the current `analysis.json`, and writes the template otherwise.
