# Setup prompt for the Lead's AI assistant (run once, before the team starts)

How to use: unzip this kit into an empty folder on the computer logged in to GitHub as `yannx8`, open Claude Code (or your agent) in that folder, and paste everything below the line.

---

You are setting up the shared foundation of **MboaScope**, a NASA Space Apps 2026 project built this weekend by six developers, each working with their own AI assistant. Your job is **not** to build the product. Your job is to create the repo, the rules, the contract, the stubs, the mock data and the issues, so that six people can work in parallel without colliding. Finish in **30 minutes**; five people are waiting.

The folder already contains the authoritative team documents. Read them first and do not rewrite their content:
`AGENTS.md`, `CLAUDE.md`, `docs/TEAM.md`, `docs/CONTRACT.md`, `docs/SCIENCE.md`, `docs/prompts/*.md`.

Rules for you: follow `AGENTS.md`; no em dashes or emojis in anything you write; ask me only when blocked on something I must provide; otherwise decide, note it, continue. Log each step's check (PASS / FAIL / UNRESOLVED with evidence) in `docs/agent/checks.md`.

## Step 1. Preflight (2 minutes)
- `gh auth status`; if scopes are missing run `gh auth refresh -s repo,workflow,project` and ask me to finish the browser step.
- Check `git`, Python 3.10+, Node 22 (20.19 minimum: current Vite refuses older versions). `make` is optional: record in `docs/agent/checks.md` whether it is installed, and run the plain commands if it is not.
- Ask me once, in one message, for the five teammates' GitHub usernames and roles. Continue without waiting; add them when I answer.

## Step 2. Create the repo
Run `git init -b main` first if the folder is not a repository yet. Then `gh repo create yannx8/MboaScope --public --source . --remote origin --description "MboaScope: is Douala getting wetter or drier? NASA IMERG rainfall trends, 2001-2025 (NASA Space Apps 2026)"`. Add topics `nasa-space-apps`, `imerg`, `rainfall`, `cameroon`. If the repo already exists, use it and never rewrite its history.

## Step 3. Scaffold (keep every file minimal)

```
pipeline/__init__.py
pipeline/common.py        # Lead: write_json(path, payload, is_mock) adds contract_version "1.0", generated_at (UTC ISO), is_mock; read_sources(); is_mock_run() from data/interim/sources.json
pipeline/config.py        # Processing: values from docs/SCIENCE.md (START_YEAR 2001, END_YEAR 2025, REGION, BOXES with labels and bounds, HEADLINE_BOX, ALPHA 0.05, DATASET dict)
pipeline/make_mock.py     # Data: WORKING now (see step 4)
pipeline/inspect_granule.py, fetch_imerg.py, import_giovanni.py, fetch_gpcp.py   # Data: stubs
pipeline/units.py, aggregate.py      # Processing: stubs
pipeline/stats.py, analyse.py        # Analytics: stubs
pipeline/explain.py, prompts/rewrite.md  # AI: stubs
pipeline/build.py                    # Lead: stub
tests/test_contract.py               # Lead: WORKING now
tests/fixtures/                      # empty, with .gitkeep
data/interim/  data/external/  data/raw/ (gitignored)
web/                                 # Frontend: minimal Vite + React app (step 6)
docs/contract/*.schema.json          # Lead: WORKING now (step 5)
docs/SUBMISSION.md  docs/METHOD.md (AI: placeholder heading only)  docs/agent/checks.md
.github/workflows/ci.yml  .github/workflows/pages.yml
.github/pull_request_template.md  .github/ISSUE_TEMPLATE/task.md
.github/copilot-instructions.md      # one line: "Follow AGENTS.md at the repo root."
.cursor/rules/project.mdc            # one line pointing to AGENTS.md (for Cursor users)
README.md  Makefile  requirements.txt  requirements-fetch.txt  .env.example  .gitignore
```

**Stubs:** each stub module contains its owner in a header comment, the exact public function signatures and CLI described in that owner's role prompt (`docs/prompts/<role>.md`), docstrings copied from the spec, and bodies that raise `NotImplementedError`. Every module has `main()` and `if __name__ == "__main__": main()`. Do not implement owners' logic.

**requirements.txt:** numpy, pandas, scipy, pymannkendall, xarray, jsonschema, python-dotenv, pytest, google-genai. **requirements-fetch.txt:** earthaccess, h5netcdf, h5py. Use `>=` minimums that you confirm install.

**.env.example:** `EARTHDATA_USERNAME=`, `EARTHDATA_PASSWORD=`, `GEMINI_API_KEY=`, `GEMINI_MODEL=`. **.gitignore:** `.env`, `data/raw/`, `node_modules/`, `web/dist/`, `__pycache__/`, `.venv/`.

**Makefile** targets exactly as in `docs/CONTRACT.md` (Python entry points) plus `setup` (venv + requirements + `npm ci` in web), `test` (pytest), `web-dev`, `web-build`, `spike` (`python -m pipeline.inspect_granule`), `fetch`, `giovanni FILE=... [ACTIVATE=1]` (passes `--activate`), `explain` and `build` honouring `LLM=1`. Every target is a thin wrapper around one `python -m ...` or `npm ...` command, because Windows teammates may not have `make`.

## Step 4. Mock data (so nobody waits)
Implement `pipeline/make_mock.py` fully: a synthetic 9 x 9 region from 2001-01 to 2025-12 in the exact `region_monthly_rate.csv` format, units `mm/hr`, a Douala-like seasonal cycle (wettest July to September, driest December to February), annual totals roughly 3,000 to 4,500 mm, random interannual noise, a small step in June 2014, fixed seed. It writes `sources.json` with `access_method: "mock"`. Run it and commit the outputs.

Then hand-write **valid fixture JSON** for all five web files in `web/public/data/` (`annual.json`, `analysis.json`, `spatial.json`, `explanation.json`, `provenance.json`) exactly following `docs/CONTRACT.md`, all with `is_mock: true`, plausible values, 25 years, 81 cells, explanation text that obeys `docs/SCIENCE.md`. These let Frontend and AI start immediately; owners replace them with generated files later.

## Step 5. Contract schemas and test
Write JSON Schemas (draft 2020-12) in `docs/contract/` for the five web files, strict on required fields, types and enums from `docs/CONTRACT.md`. `tests/test_contract.py` validates every file in `web/public/data/` and checks the interim CSV headers when the files exist. It must pass on the fixtures.

## Step 6. Minimal web app
`npm create vite@latest web -- --template react`, add `recharts`, `leaflet`, `react-leaflet`, set `base: "/MboaScope/"`. Replace the demo page with a single placeholder that loads the five JSON files from `${import.meta.env.BASE_URL}data/`, shows a red mock banner when any has `is_mock: true`, and prints the headline verdict. Create `web/src/content.js` with the page title. Nothing more: Frontend owns the rest.

## Step 7. CI and Pages
- `ci.yml` on pull requests and pushes, as one job named exactly `ci` (branch protection in step 10 matches the job name, not the file name): Python setup, `pip install -r requirements.txt`, `pytest -q`; Node setup, `npm ci && npm run build` in `web/`.
- `pages.yml` on push to `main`: build `web/`, deploy with `actions/upload-pages-artifact` and `actions/deploy-pages`. Enable Pages for workflow builds: `gh api -X POST repos/yannx8/MboaScope/pages -f build_type=workflow` (use `PUT` if it exists).

## Step 8. Templates and README
- Pull request template: `Closes #`, role, what changed, files touched (must be owned by your role), contract changed yes/no, how tested (command and output), screenshots for UI.
- Issue template: owner role, files, steps, acceptance criteria, depends on, gate, branch name.
- `README.md`: one paragraph on the question and data, "Start here" pointing to `AGENTS.md` and `docs/TEAM.md`, how to run (`make setup`, `make mock`, `make test`, `make web-dev`, and a table giving the plain command behind every `make` target for teammates without `make`), links to the live site and the board, data credit with the DOI. Challenge name: `TBD`.
- `docs/SUBMISSION.md`: the checklist from `docs/prompts/lead.md` issue #7 plus: demo of 30 seconds or less with English subtitles or 7 slides or fewer in English on a public link; deployed site and repo open from a phone; NASA data named with DOI; limitations visible; AI tool use described if the Space Apps terms ask; all members on the team page; terms box checked.

Commit as `lead: project foundation` and push to `main` (before protection is enabled).

## Step 9. Labels, milestones, issues, board
- Labels: `role:lead`, `role:data`, `role:processing`, `role:analytics`, `role:ai`, `role:frontend`, `priority:must`, `priority:should`, `contract`, `blocked`.
- Milestones: `G1 Sat 19:00 real data`, `G2 Sat 23:00 deployed`, `G3 Sun 12:00 freeze`, `G4 Sun 18:00 submitted`.
- Create the 26 issues **in the exact order** of the table in `docs/TEAM.md` section 4, so numbers match. Each body: owner role, the role prompt section to follow (`docs/prompts/<role>.md`, issue #n), files to touch, acceptance criteria copied from the role prompt, dependencies, branch name `feature/<area>-<n>-<slug>`. Labels and milestone from the table (#11 and #19 are `priority:should`). Assign when usernames are known. Verify the numbers match the table; if they do not, edit titles so they do and tell me.
- Board: `gh project create --owner yannx8 --title "MboaScope - Space Apps 2026"`, add all issues, status To do. If the `project` scope is unavailable, print the 5 manual steps.

## Step 10. Access and protection
- Invite each teammate: `gh api -X PUT repos/yannx8/MboaScope/collaborators/<user> -f permission=push`.
- Protect `main`: pull request required, status check `ci` required, no force-push, no deletion, zero required approvals (the Lead merges; speed matters). If the API refuses, print the manual steps.

## Step 11. Verify and report
Run and record: `make setup`, `make mock`, `pytest -q` (contract test passes), `npm run build`, CI green on GitHub, Pages URL loads with the mock banner, `git grep -n -i "api_key\|password"` shows variable names only (in `.env.example`, docs and code), never a value.

Reply to me with only:
1. Repo URL, Pages URL, board URL.
2. Checks table (PASS / FAIL / UNRESOLVED, one line of evidence each).
3. A message I can paste in the team WhatsApp: clone command, "read AGENTS.md and docs/TEAM.md", "paste docs/prompts/<your role>.md into your assistant", "your first issue is #n", next standup time.
4. Manual steps I still must do.
