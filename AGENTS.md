# AGENTS.md: rules for every AI assistant working on MboaScope

This file is read by Claude Code, Codex, Cursor, Copilot, Gemini CLI and any other coding agent. Humans follow it too. If anything conflicts with it, this file wins, then `docs/TEAM.md`, then your role prompt.

## Before you write any code

1. Read, in order: this file, `docs/TEAM.md`, `docs/CONTRACT.md`, `docs/SCIENCE.md`, then the role prompt your human gives you (`docs/prompts/<role>.md`).
2. Ask your human which issue number you are working on. Work on one issue at a time.
3. Write a short plan in the issue or in your reply: numbered steps, each with one output and one check. Then execute.

## Ownership (the most important rule)

- Six humans each own a set of files (table in `docs/TEAM.md`). **You edit only the files your human's role owns.**
- If you need a change in a file you do not own, stop and write a note your human can paste into a GitHub issue for the owner. Do not make the change yourself.
- `docs/CONTRACT.md`, `docs/contract/*.schema.json`, `AGENTS.md`, `CLAUDE.md`, `Makefile`, `requirements.txt`, `.github/` are owned by the Lead. Never edit them unless your human is the Lead.

## The contract

- Modules talk to each other only through the files defined in `docs/CONTRACT.md`. Produce exactly those columns and fields, with those names and units. Consume them as defined.
- Never change a field name, type or unit on your own. A contract change is an issue labelled `contract`, approved by the Lead, announced to the team.
- Every JSON in `web/public/data/` carries `contract_version`, `generated_at`, `is_mock`. Mock data is always `is_mock: true`.
- Do not commit generated outputs (`data/interim/annual_*.csv`, `web/public/data/*.json`). The Lead regenerates and commits them with `make build`. The exceptions are listed in `docs/CONTRACT.md`, "Who commits generated files".

## Git workflow

- Never commit to `main`. Branch per issue: `feature/<area>-<issue#>-<short-slug>` (for example `feature/data-7-spike`).
- Before opening a pull request: `git fetch origin && git rebase origin/main`, then `make test` (and your role's own checks). Without `make` (Windows), run the plain command instead: `python -m pytest -q`, `python -m pipeline.<module>`. Paste the command output in the pull request.
- Small pull requests, merged often (at least every 3 hours). Commit messages start with your area: `data: ...`, `processing: ...`, `analytics: ...`, `ai: ...`, `frontend: ...`, `lead: ...`.
- Fill the pull request template completely. Link the issue with `Closes #n`.

## Honesty rules (non-negotiable)

- Never invent data, numbers or results. Never hardcode a result into code, docs or UI text; numbers flow from pipeline outputs only.
- Never write that the data proves a cause, that rainfall "did not change" when a test is non-significant, that values were "measured in Douala" or "at a station", or any future prediction. Details in `docs/SCIENCE.md`.

## Engineering rules

- Python 3.10+, type hints, pure functions where possible, no network calls in tests.
- No new dependency without the Lead's approval (ask in the issue). No backend, database, auth, routing, Docker.
- Secrets only in `.env` (gitignored). Never print or commit keys or passwords.
- A failing check gets at most 3 fix attempts. Then stop, report what you tried and the exact error, and let your human escalate.
- Do not refactor, rename or "improve" code outside your issue.

## Writing style for docs, comments and UI text

Plain English, short sentences, no em dashes (use commas, colons or parentheses), no emojis.

## When you finish

Report to your human: what changed (files), how it was tested (commands and results), what is still open, and the handoff message to post (format in `docs/TEAM.md`).
