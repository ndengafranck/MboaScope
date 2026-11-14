# MboaScope

Is Douala getting wetter or drier? MboaScope tests whether NASA's GPM IMERG satellite rainfall estimates (Final run, monthly, Version 07, DOI 10.5067/GPM/IMERG/3B-MONTH/07) show a statistically detectable trend in annual rainfall over a 33 km box around Douala, Cameroon, from 2001 to 2025. It reports the answer, the uncertainty and the known data threats in plain language. Built for NASA Space Apps 2026. Challenge: `TBD`.

Live site: https://yannx8.github.io/MboaScope/
Board: `TBD` (see the project board link in the repo's Projects tab)

## Start here

Read `AGENTS.md` and `docs/TEAM.md`. Then paste your role prompt from `docs/prompts/` into your AI assistant.

## Run it

```
make setup      # venv, Python deps, npm ci in web/
make mock       # synthetic data, so nobody waits
make test       # contract and unit tests
make web-dev    # local site
```

No `make` (Windows)? Use the plain command:

| make target | Plain command |
| --- | --- |
| `make setup` | `python -m venv .venv`, then `.venv/Scripts/python -m pip install -r requirements.txt`, then `npm ci --prefix web` |
| `make mock` | `python -m pipeline.make_mock` |
| `make spike` | `python -m pipeline.inspect_granule` |
| `make fetch` | `python -m pipeline.fetch_imerg` |
| `make giovanni FILE=f.csv` | `python -m pipeline.import_giovanni f.csv` (add `--activate` for `ACTIVATE=1`) |
| `make process` | `python -m pipeline.aggregate` |
| `make analyse` | `python -m pipeline.analyse` |
| `make explain` | `python -m pipeline.explain` (add `--llm` for `LLM=1`) |
| `make build` | `python -m pipeline.build` (add `--llm` for `LLM=1`) |
| `make test` | `python -m pytest -q` |
| `make web-dev` | `npm run dev --prefix web` |
| `make web-build` | `npm run build --prefix web` |

Fetching real data needs `pip install -r requirements-fetch.txt` and a NASA Earthdata login in `.env` (see `.env.example`).

## Docs

- `docs/TEAM.md`: roles, ownership, gates, issues.
- `docs/CONTRACT.md`: the data formats between modules.
- `docs/SCIENCE.md`: methods and allowed wording.
- `docs/SUBMISSION.md`: submission checklist.

## Data credit

GPM IMERG Final Precipitation L3 1 month 0.1 degree x 0.1 degree V07 (GPM_3IMERGM), NASA GES DISC. DOI: 10.5067/GPM/IMERG/3B-MONTH/07.
