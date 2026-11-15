# MboaScope

**Has rainfall increased or decreased over time in a region of Cameroon, and is that trend statistically significant?**

MboaScope answers that question for ten study regions (one per regional capital) from NASA's GPM IMERG
satellite rainfall (Final run, monthly, Version 07, DOI 10.5067/GPM/IMERG/3B-MONTH/07). It runs
Mann-Kendall, Sen's slope and Pettitt tests, shows the uncertainty and the known data threats, and
explains the result in plain language with checked AI text. Started at NASA Space Apps 2026.

## Structure

```
backend/      FastAPI + SQLite. app/routes, app/services/{nasa,gis,analytics,ai}, app/schemas
frontend/     React + TypeScript (Vite). pages: Dashboard, Explorer, Analysis, Assistant
data/         regions/ (study regions), raw/, processed/ (SQLite, gitignored), sample/
tests/        pytest suite for the backend (no network)
docs/         architecture.md, api.md, methodology.md, TEAM.md (who does what), MIGRATION.md
```

## Run it locally

Needs Python 3.10+ and Node 20.19+.

```bash
# backend (terminal 1)
python -m venv .venv
.venv/bin/pip install -r backend/requirements.txt      # Windows: .venv\Scripts\pip
cd backend
../.venv/bin/python -m app.cli seed-mock               # demo data for all ten regions
../.venv/bin/uvicorn app.main:app --reload             # http://127.0.0.1:8000/docs

# frontend (terminal 2)
cd frontend
npm install
npm run dev                                            # http://localhost:5173
```

Tests: `python -m pytest -q` from the repository root. Frontend checks: `npm run build` in `frontend/`.
With `make`: `make setup`, `make mock`, `make api`, `make web`, `make test`.

Real NASA data needs `pip install -r backend/requirements-fetch.txt` and an Earthdata login in `.env`
(copy `.env.example`). See `docs/architecture.md`, "Data ingestion".

## Status

The full chain works on **mock data**: every page shows a "Demo data" banner until real NASA data is
ingested. Remaining work and who owns it: `docs/TEAM.md`.

## Docs

- `docs/TEAM.md`: the two developer roles and the remaining tasks.
- `docs/api.md`: the API contract between frontend and backend.
- `docs/architecture.md`: modules, request flow, design decisions.
- `docs/methodology.md`: data, methods, limitations and allowed wording.

## Data credit

GPM IMERG Final Precipitation L3 1 month 0.1 degree x 0.1 degree V07 (GPM_3IMERGM), NASA GES DISC.
DOI: 10.5067/GPM/IMERG/3B-MONTH/07.
