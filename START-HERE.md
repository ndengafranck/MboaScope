# MboaScope kit: start here (Lead only)

1. Unzip this kit into an empty folder on the computer logged in to GitHub as `yannx8`.
2. Open Claude Code in that folder and paste `SETUP-PROMPT.md` (everything below its line). It creates the repo, rules, contract, stubs, mock data, CI, site, 26 issues and the board in about 30 minutes.
3. While it runs, send the team this message:
   "Kickoff at 14:30. Before then: pick your role (Data, Processing, Analytics, AI, Frontend), send me your GitHub username, create a NASA Earthdata account (Data and Processing), a Gemini key in Google AI Studio (AI). Install Git, Python 3.10+, Node 22 and your AI assistant. On Windows you do not need make: the README lists the plain commands."
4. At kickoff, everyone clones, reads `AGENTS.md` and `docs/TEAM.md`, and pastes their own `docs/prompts/<role>.md` into their assistant, starting with the first issue in their role.
5. After setup, paste `docs/prompts/lead.md` into your own assistant for your Lead work.

Files:
- `AGENTS.md`: rules every AI assistant follows (Claude, Codex, Cursor, Copilot, Gemini).
- `docs/TEAM.md`: roles, file ownership, gates, the 26 issues, rhythm, git rules, fallbacks.
- `docs/CONTRACT.md`: the data formats between modules.
- `docs/SCIENCE.md`: data, methods and allowed wording.
- `docs/prompts/`: one prompt per role.
