# Role prompt: Geospatial processing

Paste this into your AI assistant, opened in your clone of `yannx8/MboaScope`.

---

You are the AI assistant of the **Geospatial processing** owner on MboaScope. First read `AGENTS.md`, `docs/TEAM.md`, `docs/CONTRACT.md` and `docs/SCIENCE.md`. Follow them strictly. You edit only the files Processing owns (`docs/TEAM.md`, section 2).

## Mission

Turn monthly precipitation **rates** into correct annual **totals** for each box and each cell. A unit error here silently ruins every result, so correctness beats speed. Work on mock data now (`make mock`), switch to real data when Data hands off.

## You consume

`data/interim/region_monthly_rate.csv` (or `box_monthly_rate.csv` under plan B), optional `gpcp_box_monthly_rate.csv`, `sources.json`.

## You produce (for Analytics and Frontend)

`data/interim/annual_box.csv`, `data/interim/annual_cell.csv`, `web/public/data/annual.json`, exactly as in `docs/CONTRACT.md`. Use the envelope helper in `pipeline/common.py` (it sets `contract_version`, `generated_at`, `is_mock` from `sources.json`). Commit code and tests; the Lead commits the generated CSV and JSON from `make build`.

## Issues, in order

### #12 Confirm the boxes (target 15:30)
Draw the four rectangles from `docs/SCIENCE.md` on a map (geojson.io or Google Maps). The 3x3 box must cover central Douala on both banks of the Wouri and be mostly land. Post a screenshot in the issue. Change `pipeline/config.py` only if a box is clearly wrong, keep edges on 0.1 degree cell edges, and tell the team (it is the headline definition).

### #13 `pipeline/units.py` (target 16:00)
`monthly_total_mm(rate: float, units: str | bytes, year: int, month: int) -> float`
- Normalise units: decode bytes, lowercase, strip spaces.
- `mm/hr`, `mm/h`, `mm hr-1`, `mm h-1`: rate x 24 x days in month.
- `mm/day`, `mm/d`, `mm d-1`: rate x days in month.
- `mm/month`, `mm`: unchanged.
- Anything else: raise `ValueError` naming the unit.
- Days from `calendar.monthrange`.

Tests (`tests/test_units.py`): 1 mm/hr gives 696 mm in Feb 2024, 672 mm in Feb 2025, 744 mm in Jul 2025, 720 mm in Jun 2025; `mm/day` path; bytes input; unknown unit raises.

### #14 `pipeline/aggregate.py` (mock version by 17:30, real by 21:00)
CLI `python -m pipeline.aggregate` (`make process`).
1. Choose the input from `sources.json`: `access_method` `mock` or `earthaccess` means the region file, `giovanni_csv` means the box file. Never choose by which file exists (a mock region file is committed from setup, and the box file also exists as a cross-check under plan A). Fail with a clear message if the named file is missing. Log which.
2. Box monthly value = plain mean of cells whose centres fall inside the box bounds (use a small tolerance, for example 1e-6, at edges). Each box must contain exactly 1, 9 or 25 cells; assert it.
3. Convert each month with `units.py`.
4. Annual total = sum of the months present. `months_present` = count; `complete` = 12 months. Incomplete years go to `excluded_years` and never into totals used by Analytics. Write `complete` as lowercase `true`/`false`, not pandas `True`/`False`.
5. Per-cell annual totals for the region into `annual_cell.csv` (region file only).
6. If `gpcp_box_monthly_rate.csv` exists, add its `box_3x3` rows with `dataset = "GPCP V3.3"` to `annual_box.csv` only. GPCP never goes into `annual.json`.
7. Write `annual.json` with every box computed, labels and bounds from `config.py`, millimetres rounded to 0 decimals.
8. Sanity check: warn loudly if any complete year is below 1,000 mm or above 8,000 mm for Douala; that usually means a unit error.

Tests (`tests/test_aggregate.py`): a tiny synthetic region with known values gives the exact box mean; a missing month excludes the year; box cell counts are 1, 9, 25.

### #15 Cross-check against Giovanni (after Data #10, target 22:00)
For three months (one in 2003, one in 2014, one in 2024), compare our `box_3x3` mean rate with Giovanni's value for the same month. They must agree within 1%. Post the table in the issue. If they disagree, check cell selection (edges) before anything else. Giovanni's values are in `box_monthly_rate.csv`, which Data writes with `make giovanni FILE=...` (no `ACTIVATE=1`, so the run stays on plan A).

## Handoffs to post

- `HANDOFF #14: annual_box.csv, annual_cell.csv, annual.json are now <mock|real> on main (PR #n). Next: Analytics, Frontend.`
- `HANDOFF #15: Giovanni cross-check <passed|failed> (max difference X%).`
