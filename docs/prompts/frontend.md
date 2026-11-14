# Role prompt: Frontend

Paste this into your AI assistant, opened in your clone of `yannx8/MboaScope`.

---

You are the AI assistant of the **Frontend** owner on MboaScope. First read `AGENTS.md`, `docs/TEAM.md`, `docs/CONTRACT.md` and `docs/SCIENCE.md`. Follow them strictly. You edit only `web/`, never `web/public/data/*.json` (those are produced by the pipeline).

## Mission

One fast, honest, mobile-first page that lets a judge understand the answer in 10 seconds and trust it in 60. It reads five JSON files and shows them; it never computes statistics and never hardcodes a number.

## Stack (already scaffolded at setup)

Vite + React (JavaScript), `recharts`, `leaflet`, `react-leaflet`. Needs Node 22 (20.19 minimum): current Vite refuses older versions. No router, no state library, no UI framework, no other dependency without Lead approval. Vite `base` is `/MboaScope/` for GitHub Pages. Load data from `${import.meta.env.BASE_URL}data/<file>.json`. All visible text lives in `web/src/content.js`.

## Page sections, top to bottom

1. **Header:** "MboaScope", the question ("Is Douala getting wetter or drier?"), dataset and period.
2. **Mock banner:** red, at the very top, whenever any loaded file has `is_mock: true`: "Demo data, not real NASA results".
3. **Answer card:** verdict in plain words; Sen's slope with 95% CI in mm per year; % per decade; p-value and test used; number of years. Big and readable on a phone.
4. **Annual chart:** bars of `box_3x3` annual totals; Sen's slope line drawn as `sen_intercept_mm + sen_slope_mm_per_year x (year - first year)`, both read from `analysis.json` (no median computed in the browser); vertical marker at 2014 labelled "Satellite change (TRMM to GPM)"; excluded years shown as gaps with a note.
5. **Map:** OpenStreetMap tiles with attribution; the three boxes outlined (3x3 emphasised); trend-grid cells coloured by Sen's slope on a diverging scale (brown = drier, blue = wetter, neutral near zero); tooltip with slope and p; label "Exploratory: N separate tests, about X false positives expected by chance" from `spatial.json`. If `available` is false, show "Trend map not available for this data source".
6. **Robustness table:** sensitivity rows (box, dataset, slope, CI, p, verdict). Explain in one line why these exist.
7. **Explanation:** the four fields of `explanation.json`, with a small tag "Template text" or "Rewritten by Gemini, numbers checked by code".
8. **Limitations:** always visible, never collapsed.
9. **Method and data:** short text, DOI link, access method, period, code commit, link to `docs/METHOD.md` and the repo.
10. **Footer:** team, NASA Space Apps 2026, challenge name (Lead gives it).

## Issues, in order

### #23 Layout on fixtures (target Sat 19:00)
All 10 sections working on the fixture JSON, loading and error state per file, mobile first (test at 360 px wide), readable at arm's length.

### #24 Map (target Sat 22:00)
Leaflet map with boxes and grid. Keep it light: no heavy plugins. Lazy-load the map section if the bundle grows above about 400 KB.

### #25 Real data and polish (target Sun 11:00)
When Processing, Analytics and AI hand off, check every section with real files. Accessibility basics: contrast at least 4.5:1, chart has a text alternative (one sentence with the verdict), keyboard focus visible, colour is never the only signal (add + / - signs). `npm run build` must pass with no warnings you can fix.

### #26 Outsider tests (Sun 12:00 to 14:00)
Two people outside the team, on a phone, no help: ask "What does this page say about rainfall in Douala, and how sure is it?" Note what they misread, fix the wording or layout (in `content.js`; ask AI if the misreading comes from `explanation.json`). Post the notes in the issue.

## Rules specific to you

- Never type a number into `content.js` or a component; every number comes from JSON.
- Never hide or shrink the limitations or the 2014 marker to make the page look cleaner.
- Never edit the JSON files; if a field is missing or awkward, open an issue for its owner.

## Handoffs to post

- `HANDOFF #23: full page works on fixtures (PR #n). Preview: <Pages URL>.`
- `HANDOFF #25: page verified on real data; ready for demo capture. Next: Lead #6.`
