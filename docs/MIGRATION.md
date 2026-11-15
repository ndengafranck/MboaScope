# Migration from the hackathon layout

The restructure is on branch `restructure/fastapi-react-mvp`. History is kept (`git log --follow` works
on moved files). This page maps every old location to its new one.

## Code

| Before | After | What changed |
| --- | --- | --- |
| `pipeline/units.py` | `backend/app/services/nasa/units.py` | nothing |
| `pipeline/make_mock.py` | `backend/app/services/nasa/mock.py` | all ten regions, writes to SQLite |
| `pipeline/import_giovanni.py` | `backend/app/services/nasa/giovanni.py` | `--region`, writes to SQLite |
| `pipeline/fetch_imerg.py` (stub) | `backend/app/services/nasa/fetch_imerg.py` | first implementation, untested (task A1) |
| `pipeline/inspect_granule.py` (stub) | `backend/app/services/nasa/inspect_granule.py` | first implementation, untested (task A1) |
| `pipeline/fetch_gpcp.py` (stub) | `backend/app/services/nasa/fetch_gpcp.py` | still a stub (task A8) |
| `pipeline/config.py` | `backend/app/core/config.py` + `data/regions/cameroon_study_regions.json` + `services/gis/regions.py` | boxes are computed per region |
| `pipeline/aggregate.py` | `backend/app/services/gis/spatial.py` | returns data frames instead of writing CSV/JSON |
| `pipeline/stats.py` | `backend/app/services/analytics/stats.py` | **bug fix:** `mk_hamed_rao` ran the original test |
| `pipeline/analyse.py` | `backend/app/services/analytics/trends.py` | region-aware caveats |
| `pipeline/explain.py` | `backend/app/services/ai/interpreter.py` | any region; 3 or 4 limitations; `interpret()` and `suggest_investigations()` for the API |
| `pipeline/prompts/rewrite.md` | `backend/app/services/ai/prompts/rewrite.md` | limitation count no longer fixed at 4 |
| `pipeline/common.py` | `backend/app/core/config.py` | |
| `pipeline/build.py` | removed | the API runs the chain on request |
| `check_mk.py` | `backend/scripts/check_mann_kendall.py` | reads from the API services; key bug (`S`) fixed |
| `web/` (React, JSX) | `frontend/` (React, TypeScript) | four pages, calls the API instead of static JSON |
| `requirements*.txt` | `backend/requirements*.txt` | FastAPI and uvicorn added, jsonschema removed |

## Data

| Before | After |
| --- | --- |
| `data/interim/region_monthly_rate.csv` | `observations` table |
| `data/interim/box_monthly_rate.csv` | `box_observations` table |
| `data/interim/sources.json` | `sources` table, one row per region |
| `data/interim/annual_*.csv` | computed on request |
| `web/public/data/*.json` | API responses (`docs/api.md`) |
| `data/external/` | `data/raw/` |

## Docs

| Before | After |
| --- | --- |
| `docs/SCIENCE.md` + `docs/METHOD.md` | `docs/methodology.md` |
| `docs/CONTRACT.md` + `docs/contract/*.schema.json` | `docs/api.md` + `backend/app/schemas/` |
| `docs/TEAM.md` (six roles) | `docs/TEAM.md` (two developers) |
| `docs/prompts/*.md` (six role prompts) | removed; tasks are in `docs/TEAM.md` |
| `eval.md` | `docs/ai-eval.md` |
| `SETUP-PROMPT.md`, `START-HERE.md`, `docs/agent/checks.md`, `.cursor/` | removed (hackathon kit) |
| (new) | `docs/architecture.md`, this file |

## Things to do once after merging

1. Recreate your virtual environment: `pip install -r backend/requirements.txt`.
2. `cd backend && python -m app.cli seed-mock` to build the local database.
3. `cd frontend && npm install`.
4. Close the old six-role issues and open the A and B tasks from `docs/TEAM.md`.
5. Rotate the Gemini key and the Earthdata password if the old project zip, which contained `.env`,
   was shared with anyone.
