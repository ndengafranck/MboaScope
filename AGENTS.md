# AGENTS.md: rules for every AI assistant working on MboaScope

Read by Claude Code, Codex, Cursor, Copilot, Gemini CLI and any other coding agent. Humans follow it too.
If anything conflicts with it, this file wins, then `docs/TEAM.md`.

## Before you write any code

1. Read, in order: this file, `docs/TEAM.md`, `docs/architecture.md`, `docs/api.md`, `docs/methodology.md`.
2. Ask your human which task (A1, B3, ...) you are working on. One task at a time.
3. Write a short plan: numbered steps, each with one output and one check. Then execute.

## Ownership

- Two developers. Developer A owns data, science and the backend; Developer B owns the frontend and the
  AI module. The exact file list is in `docs/TEAM.md`, section 1. **Edit only files your human owns.**
- Need a change elsewhere? Stop and write a note your human can paste into an issue for the owner.
- The API contract is three files changed together: `backend/app/schemas/*.py`,
  `frontend/src/types/api.ts`, `docs/api.md`. Never change one without the others.

## Science and honesty rules (non-negotiable)

- Never invent data, numbers or results. Never hardcode a result into code, docs or UI text.
- The frontend never recomputes statistics; it displays what the API returns.
- Never write that the data proves a cause, that rainfall "did not change" when a test is non-significant,
  that values were "measured in" a city or "at a station", or any prediction. Details: `docs/methodology.md`.
- Mock data must stay flagged (`is_mock: true`) and the demo banner must show.

## Engineering rules

- Python 3.10+, type hints, pure functions in `services/`, no network calls in tests.
- TypeScript strict mode; all API calls go through `frontend/src/services/api.ts`.
- New dependency: ask the other developer in the issue first.
- Secrets only in `.env` (gitignored). Never print or commit keys or passwords.
- A failing check gets at most 3 fix attempts. Then stop and report the exact error.
- Do not refactor code outside your task.

## Git workflow

- Never commit to `main`. Branch per task: `feature/a-<task>-<slug>` or `feature/b-<task>-<slug>`.
- Before a pull request: `git fetch origin && git rebase origin/main`, `python -m pytest -q`, and for
  frontend changes `npm run build` in `frontend/`. Paste the output in the pull request.
- Commit messages start with the area: `data:`, `gis:`, `analytics:`, `api:`, `frontend:`, `ai:`.

## Writing style for docs, comments and UI text

Plain English, short sentences, no em dashes, no emojis.
