# MboaScope team playbook (NASA Space Apps 2026, 14-15 November)

Six developers, one repo, one contract. Each developer works with their own AI assistant, which must follow `AGENTS.md`. All times are Douala time (UTC+1).

## 1. Roles and owners

| Role | Name | GitHub | Branch prefix | Role prompt |
| --- | --- | --- | --- | --- |
| Lead and integration | Yann | yannx8 | `feature/lead-` | `docs/prompts/lead.md` |
| Data engineering | Firmin | Firminfire | `feature/data-` | `docs/prompts/data.md` |
| Geospatial processing | Theophile | excellenttheophile | `feature/processing-` | `docs/prompts/processing.md` |
| Scientific analysis | Bako | yannsamir22 | `feature/analytics-` | `docs/prompts/analytics.md` |
| AI engineering | Franck | ndengafrank | `feature/ai-` | `docs/prompts/ai.md` |
| Frontend | Pavel | Paveljuniorr | `feature/frontend-` | `docs/prompts/frontend.md` |

Pick roles by strongest skill at kickoff. If the team is five, Data and Processing merge into one person. Whoever planned to do "backend" takes Data or Processing: there is no backend.

## 2. File ownership (only the owner edits; others open an issue)

| Role | Owns |
| --- | --- |
| Lead | `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/TEAM.md`, `docs/CONTRACT.md`, `docs/contract/`, `docs/SUBMISSION.md`, `Makefile`, `requirements*.txt`, `.github/`, `pipeline/common.py`, `pipeline/build.py`, `tests/test_contract.py`, `web/public/data/provenance.json` |
| Data | `pipeline/fetch_imerg.py`, `pipeline/import_giovanni.py`, `pipeline/inspect_granule.py`, `pipeline/make_mock.py`, `pipeline/fetch_gpcp.py`, `data/interim/region_monthly_rate.csv`, `data/interim/box_monthly_rate.csv`, `data/interim/sources.json`, `tests/test_data_*.py` |
| Processing | `pipeline/config.py`, `pipeline/units.py`, `pipeline/aggregate.py`, `data/interim/annual_box.csv`, `data/interim/annual_cell.csv`, `web/public/data/annual.json`, `tests/test_units.py`, `tests/test_aggregate.py` |
| Analytics | `pipeline/stats.py`, `pipeline/analyse.py`, `web/public/data/analysis.json`, `web/public/data/spatial.json`, `tests/test_stats.py`, `tests/test_analyse.py` |
| AI | `pipeline/explain.py`, `pipeline/prompts/`, `web/public/data/explanation.json`, `docs/METHOD.md`, `tests/test_explain.py` |
| Frontend | everything in `web/` except `web/public/data/*.json` |

Owning a generated file means your code is the only code that writes it. Who commits it is a separate rule: see "Who commits generated files" in `docs/CONTRACT.md` (short version: you commit code and tests, the Lead commits the outputs).

## 3. Gates (hard deadlines)

| Gate | Time | Definition of done |
| --- | --- | --- |
| G0 | Sat 14:30 | Repo, contract, fixtures, issues ready; everyone cloned and running their assistant |
| G1 | Sat 19:00 | Real IMERG monthly data on `main` (plan A or B); every module works on mock data and has tests |
| G2 | Sat 23:00 | `make build` on real data; site deployed with real numbers |
| G3 | Sun 12:00 | Results frozen, tag `v1.0-results`; no pipeline change after this |
| G4 | Sun 18:00 | Demo published and project submitted |

## 4. Issues (created in this order, so numbers are fixed)

| # | Owner | Issue | Gate |
| --- | --- | --- | --- |
| 1 | Lead | Kickoff: confirm the official challenge, fill names in TEAM.md, brief the team | G0 |
| 2 | Lead | Board, branch protection, push access for all six verified | G0 |
| 3 | Lead | `build.py`: run the chain, write provenance, validate all JSON; CI runs `make build` on mock | G2 |
| 4 | Lead | Integration duty: merge pull requests within 30 minutes, check each gate | G1-G3 |
| 5 | Lead | Freeze: tag `v1.0-results` after Analytics and AI sign off | G3 |
| 6 | Lead | Demo: 30-second video with English subtitles or 7 slides in English | G4 |
| 7 | Lead | Submission page complete and submitted | G4 |
| 8 | Data | Spike: one real granule, inspect structure and units, confirm Dec 2025 exists | G1 |
| 9 | Data | Full fetch of the region, 2001 to END_YEAR | G1 |
| 10 | Data | Plan B ready: Giovanni importer plus the Giovanni CSV for `box_3x3` committed as cross-check | G1 |
| 11 | Data | Should: GPCP V3.3 monthly for `box_3x3` | G3 |
| 12 | Processing | Confirm boxes on a map; adjust `config.py` only if needed | G1 |
| 13 | Processing | `units.py` with tests | G1 |
| 14 | Processing | `aggregate.py`: annual CSVs and `annual.json` (mock by G1, real by G2) | G1-G2 |
| 15 | Processing | Cross-check one month against Giovanni, within 1% | G2 |
| 16 | Analytics | `stats.py` with tests | G1 |
| 17 | Analytics | `analyse.py`: headline, sensitivity, trend map | G2 |
| 18 | Analytics | Real-result note for AI and demo, plus second-implementation check | G3 |
| 19 | Analytics | Should: GPCP sensitivity row | G3 |
| 20 | AI | Template explanation with number and claim checks | G2 |
| 21 | AI | Gemini rewrite, offline, checked; 6 test cases | G3 |
| 22 | AI | `docs/METHOD.md` and limitations text final | G3 |
| 23 | Frontend | One-page layout on fixtures, mobile first | G1 |
| 24 | Frontend | Map with boxes and exploratory trend grid | G2 |
| 25 | Frontend | Real data, polish, accessibility | G3 |
| 26 | Frontend | Two outsider tests and fixes | G4 |

Target times inside a gate are in the role prompts. If a prompt and this table disagree, this table wins.

## 5. Who waits for whom (and how not to wait)

```
Data #8 -> #9 -> Processing #14 (real) -> Analytics #17 (real) -> AI #20/#21 (real) -> Frontend #25
```

Data does #10 (the Giovanni download, about 30 minutes) right after the spike #8 and before the full fetch #9: it already gives the headline box and makes plan B real before the slow step starts.

Nobody waits: fixtures in `web/public/data/` and `make mock` exist from G0, so every module is built and tested on mock data first, then switched to real data when the upstream handoff arrives.

## 6. Daily rhythm

- **Standups (10 minutes, everyone, in person or call):** Sat 14:30, 17:00, 19:00, 21:00, 23:00; Sun 08:30, 12:00, 15:00, 17:30. Each person: done, next, blocked. Decisions go in the issue, not only in chat.
- **Team chat (WhatsApp):** blockers, handoffs, gate status. Nothing else.
- **Handoff message** (post in chat and as an issue comment):
  `HANDOFF #<issue>: <file> is now <mock|real> on main (PR #<n>). Next: <role>.`
- **Build message** (Lead, after regenerating the outputs):
  `BUILD: outputs regenerated on main (PR #<n>), is_mock=<true|false>.`
  A handoff means your code is merged. Downstream owners switch to real data after the next build message.
- **Blocked more than 45 minutes:** say it in chat; the Lead reassigns or switches to the fallback.
- **Sleep:** at least 6 hours each, in shifts. Nobody merges pipeline changes alone at night.

## 7. Git rules

1. Never commit to `main`; it is protected.
2. One branch per issue: `feature/<area>-<issue#>-<slug>`.
3. Rebase on `origin/main`, run `make test` (without `make`: `python -m pytest -q`), then open a pull request with the template filled and `Closes #n`.
4. CI must be green. The Lead merges (or a second teammate if the Lead is busy for more than 30 minutes).
5. Merge at least every 3 hours. Small pull requests beat big ones.
6. Edit only your own files. Contract changes go through an issue labelled `contract`.

## 8. Fallbacks (decided in advance, no debate)

| Trigger | Fallback | Who decides |
| --- | --- | --- |
| Sat 18:00 and no real data from plan A | Plan B: Giovanni CSV for `box_3x3` (`make giovanni FILE=... ACTIVATE=1`); trend map marked unavailable | Data + Lead |
| December 2025 granule not published | `END_YEAR = 2024` | Data tells Processing |
| Gemini key missing, quota hit, or checks fail | Ship the template explanation | AI |
| GitHub Pages fails | Deploy `web/dist` to Vercel or Netlify | Lead |
| A teammate is absent or stuck | Lead reassigns the issue; Data and Processing merge first | Lead |
| A module is late at G2 | Ship without it if it is a "should"; otherwise everyone helps the owner | Lead |

## 9. Definition of done for any issue

Code merged on `main`, tests added and green in CI, outputs match `docs/CONTRACT.md`, handoff posted, issue closed.
