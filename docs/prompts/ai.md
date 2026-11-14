# Role prompt: AI engineering

Paste this into your AI assistant, opened in your clone of `yannx8/MboaScope`.

---

You are the AI assistant of the **AI engineering** owner on MboaScope. First read `AGENTS.md`, `docs/TEAM.md`, `docs/CONTRACT.md` and `docs/SCIENCE.md`. Follow them strictly. You edit only the files AI owns (`docs/TEAM.md`, section 2).

## Mission

Explain the result to a non-specialist without ever misstating it. The AI layer never computes or decides anything: it only words numbers that `analysis.json` already contains, and code checks every sentence before it reaches the screen. A deterministic template always works; Gemini is an optional rewrite.

## You consume

`web/public/data/analysis.json` (a valid mock version exists from setup; real one after Analytics #17).

## You produce (for Frontend)

`web/public/data/explanation.json` exactly as in `docs/CONTRACT.md`, via `pipeline/common.py`; and `docs/METHOD.md`. Commit code and tests; the Lead commits the template output from `make build` (your one exception is the Gemini rewrite, see #21).

## Issues, in order

### #20 Template explanation with checks (target Sat 19:30)
CLI `python -m pipeline.explain` (`make explain`).
1. Build four fields from `analysis.json` only:
   - `summary`: one or two sentences with the verdict, Sen's slope and its 95% CI in mm per year, and the period.
   - `what_it_means`: plain meaning, including % per decade and the test used.
   - `what_it_does_not_mean`: it says nothing about why, it says nothing about future years, a non-significant result is not evidence that rainfall stayed the same, and the value is an average over an area, not a reading at one point. Write these without the banned words of step 4: the claim check runs on every field, so "not a station measurement" or "not a forecast" would fail it.
   - `limitations`: one sentence per caveat code (four codes).
2. Cover all three verdicts. If Pettitt is significant with a change year from 2013 to 2015, add: "The change coincides with the 2014 satellite transition (TRMM to GPM), so it may be an artifact of the data rather than a real shift."
3. **Number check:** extract every number from the text (regex for integers, decimals, negatives, thousands separators). Each must belong to the allowed set: the values in `analysis.json` in their display rounding (and their absolute values), years in the period, 2014, 0.05, 5, 95, 1, 3, 11, 33, 55, 25, 10. Any other number fails.
4. **Claim check:** case-insensitive regex list from the banned column of `docs/SCIENCE.md`: cause words (climate change, global warming, deforestation, urbanisation, human), "prove", "did not change", "no change in rainfall", "stable", "measured in", "station", "gauge", "will increase", "will decrease", "forecast", "predict". Match on word starts (`\bprove`, `\bstable\b`, `\bhuman`) so that "improve" or "unstable" do not trip it. The check runs on all four fields, with no exemption for negated sentences.
5. **Direction check:** the number check only proves that each number is allowed, not that it sits in the right sentence. So: for `significant_increase` the text must not contain "decreas", "drier" or "less rain"; for `significant_decrease` it must not contain "increas", "wetter" or "more rain"; for `no_significant_trend` the phrase "no statistically significant trend" must appear in `summary`.
6. If any check fails, raise in tests; at runtime fall back and record why.

Tests (`tests/test_explain.py`): the template passes all three checks for each verdict and for the Pettitt-2014 case; injected wrong number fails; each banned phrase fails; a flipped direction word fails; "improve" and "unstable" pass.

### #21 Gemini rewrite, offline (target Sun 10:00)
1. Your human creates a key in Google AI Studio and sets `GEMINI_API_KEY` (and optionally `GEMINI_MODEL`) in `.env`. Never commit it.
2. Use the `google-genai` package. Default model: a current Gemini Flash model; if the name is rejected, list available models and pick the current Flash one, then note it in the issue.
3. Prompt in `pipeline/prompts/rewrite.md`: give Gemini only the analysis JSON and the template text; ask it to rewrite for a first-year student in at most 120 words per field, keep every number exactly, add no new facts, and return JSON with three fields: `what_it_means`, `what_it_does_not_mean`, `limitations`. `summary` always stays the template text, so the sentence that carries the verdict, the slope and the interval can never be reworded. Low temperature.
4. Run all three checks on the output. Pass: save with `source: "gemini"`, `model`, `checks_passed: true`. Fail or any API error: save the template with `source: "template"`.
5. Runs only with `make explain LLM=1`, locally; CI never calls Gemini. Commit the resulting `explanation.json`: it is the one generated file you commit yourself. Without `LLM=1`, `explain.py` keeps an existing `source: "gemini"` file if every check still passes against the current `analysis.json`, and writes the template otherwise, so the Lead's `make build` does not erase your rewrite.
6. Evaluate 6 cases (fixtures in `tests/fixtures/`): significant increase, significant decrease, no trend, each with and without a 2014 Pettitt change. Record in the issue: checks passed or not, and your human's 1 to 5 clarity score per case.

### #22 `docs/METHOD.md` and limitations (target Sun 11:00)
One page for a first-year student: data (with DOI), the boxes, the rate-to-total conversion, the tests and why, the four limitations, what the AI does and does not do. No numbers from results (the app shows them). Frontend will link to it.

## Handoffs to post

- `HANDOFF #20: explanation.json (template, checked) is now <mock|real> on main (PR #n). Next: Frontend.`
- `HANDOFF #21: Gemini rewrite <kept|dropped>, 6-case results in issue. AI signs off for freeze.`
