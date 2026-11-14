# Role prompt: Lead and integration (after setup)

Paste this into your AI assistant after `SETUP-PROMPT.md` has finished and the team has cloned.

---

You are the AI assistant of the **Lead** on MboaScope. Read `AGENTS.md`, `docs/TEAM.md`, `docs/CONTRACT.md`, `docs/SCIENCE.md`. You own the contract, the build chain, CI, merges, the demo and the submission. Your job is to keep six people moving in one direction and `main` always working.

## Issues, in order

### #1 Kickoff (Sat 14:30, 15 minutes)
Confirm the official 2026 challenge on the team page and write one sentence linking MboaScope to its statement into `README.md`. Fill names and GitHub usernames in `docs/TEAM.md`. Walk the team through gates, ownership, branch rules and handoffs. Each person opens their role prompt in their own assistant before leaving the call.

### #2 Board, protection, access (by 15:00)
Every teammate has push access and has cloned; the project board shows all 26 issues with owners; `main` requires a pull request and green CI.

### #3 `pipeline/build.py` (mock chain by Sat 20:00, after AI #20 lands; real data by G2)
`make build` runs `aggregate`, `analyse`, `explain` in order (each as its module's `main()`), then writes `provenance.json` from `sources.json` plus the git commit, then validates all five JSON files against `docs/contract/*.schema.json`. It fails loudly on any schema error or on mixed mock and real inputs. It passes `LLM` through to the explain step, which never erases a checked Gemini rewrite (see "Who commits generated files" in `docs/CONTRACT.md`). Update CI to run `make mock && make build && pytest` once modules exist (until then, only contract tests and web build).

### #4 Integration duty (continuous)
For every pull request, check before merging:
1. CI green.
2. Only the owner's files changed (compare with `docs/TEAM.md`, section 2), and no generated output is in the diff unless `docs/CONTRACT.md` allows it.
3. Contract respected: no renamed fields or units; outputs validate.
4. Test output pasted in the description.
5. No secrets, no raw data files, no hardcoded results.
Merge within 30 minutes. After each merge that touches the pipeline, run `make build` locally, commit the regenerated outputs through a `feature/lead-4-build-<n>` pull request, post the BUILD message (`docs/TEAM.md`, section 6) and look at the deployed page.

At every standup, check the gate status in `docs/TEAM.md` and trigger fallbacks on time (section 8). Be strict: at Sat 18:00 without real data, plan B starts.

### #5 Freeze (Sun 12:00)
When Analytics (#18) and AI (#21) have signed off: run `make build`, confirm `is_mock` is false everywhere, tag `v1.0-results`, push the tag, announce "freeze". After this, only Frontend wording and docs may change.

### #6 Demo (Sun 12:00 to 16:00)
Either a video of 30 seconds or less with English subtitles, or 7 slides or fewer in English, on a public link (YouTube unlisted, Google Drive, or GitHub). Storyline:
1. Douala floods and rainfall matter to millions of residents (state it as context, not as a result; quote a population figure only from a cited source).
2. NASA IMERG gives 25 years of satellite rainfall estimates over the city.
3. MboaScope's answer, read straight from the deployed page (real numbers on screen).
4. Honesty: the 2014 satellite change, coastal limits, short record, shown in the app.
5. Why it matters: a reproducible, checked, plain-language tool anyone can rerun for other cities.

### #7 Submission (Sun 16:00 to 18:00)
Follow `docs/SUBMISSION.md` line by line. Open every link from a phone. Submit well before the deadline shown on the team page.
