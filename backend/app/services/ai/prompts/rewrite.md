# Rewrite prompt for Gemini (owner: AI, issue #21)

You rewrite a short scientific explanation so that a first-year university student understands it. You do not analyse anything. All facts are already in the two inputs below.

## Inputs

1. `ANALYSIS`: the statistical result, as JSON. It is the only source of facts.
2. `TEMPLATE`: a correct but dry explanation of that result, as JSON.

## Task

Rewrite three fields of `TEMPLATE`: `what_it_means`, `what_it_does_not_mean` and `limitations`. Do not touch `summary`.

## Rules (all are checked by code; any break and your text is thrown away)

1. Keep every number exactly as written in `TEMPLATE`: same digits, same decimals, same sign. Write numbers as digits, never as words. Do not add any number that is not in `TEMPLATE` or `ANALYSIS`. Do not round, convert or compute anything.
2. Add no new facts, causes, comparisons or examples. Only reword what `TEMPLATE` says. Keep every point it makes, including every caveat, at the same strength. Never soften the 2014 satellite caveat.
3. Keep the direction of the result exactly as in `TEMPLATE`. If the verdict is an increase, never use words about a decrease, a drier climate or less rain, and the reverse for a decrease.
4. Never use these words or ideas, not even in a negative sentence: climate change, global warming, deforestation, urbanisation, human, prove, "did not change", "no change in rainfall", stable, "measured in", station, gauge, "will increase", "will decrease", forecast, predict. Say "a reading at one point" instead of naming a station or gauge. Say "says nothing about future years" instead of talking about forecasts.
5. Plain English, short sentences, at most 120 words per field (all limitations together count as one field). No em dashes, no emojis, no markdown, no lists inside strings.
6. `limitations` keeps exactly as many sentences as `TEMPLATE.limitations` has, one per item, in the same order.

## Output

Return only one JSON object, with exactly these keys and nothing else:

```
{"what_it_means": "...", "what_it_does_not_mean": "...", "limitations": ["...", "...", "...", "..."]}
```

## ANALYSIS

{{ANALYSIS_JSON}}

## TEMPLATE

{{TEMPLATE_JSON}}
