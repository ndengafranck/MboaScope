// All visible text lives here (owner: Frontend).
// Rule: no number is ever typed in this file. Every number comes from the JSON
// files and is passed in to the small functions below.
// Wording follows the allowed / banned table in docs/SCIENCE.md.

export const content = {
  // 1. Header
  title: 'MboaScope',
  question: 'Is Douala getting wetter or drier?',
  subtitle: 'What NASA satellite rainfall estimates say about the Douala area, and how sure we can be.',
  headerDataset: (shortName, version) => `NASA GPM IMERG Final, monthly, version ${version} (${shortName})`,
  headerPeriod: (start, end) => `${start} to ${end}`,
  datasetLabel: 'Dataset',
  periodLabel: 'Period',

  // 2. Mock banner
  mockBanner: 'Demo data, not real NASA results',
  mockBannerDetail: 'These numbers come from a synthetic test run. They will be replaced by the real satellite record.',

  // Generic states
  loading: 'Loading...',
  errorFile: (file) => `Could not load ${file}.json. This part of the page is unavailable.`,

  // 3. Answer card
  answerHeading: 'The answer',
  verdict: {
    significant_increase: 'The satellite record shows a statistically significant increase in annual rainfall.',
    significant_decrease: 'The satellite record shows a statistically significant decrease in annual rainfall.',
    no_significant_trend: 'No statistically significant trend was detected in annual rainfall.',
  },
  verdictShort: {
    significant_increase: 'Significant increase',
    significant_decrease: 'Significant decrease',
    no_significant_trend: 'No significant trend',
  },
  verdictSymbol: {
    significant_increase: '+',
    significant_decrease: '-',
    no_significant_trend: '~',
  },
  verdictUnknown: 'Verdict not available.',
  slopeLabel: 'Estimated change',
  slopeUnit: 'mm per year',
  ciText: (lo, hi) => `95% confidence interval: ${lo} to ${hi} mm per year`,
  ciCrossesZero: 'The interval includes zero: the data are compatible with no change.',
  pctLabel: 'Relative change',
  pctUnit: '% per decade',
  pLabel: 'p-value',
  testLabel: 'Test used',
  yearsLabel: 'Years analysed',
  meanLabel: 'Mean annual total',
  mmUnit: 'mm',
  tests: {
    original: 'Mann-Kendall',
    hamed_rao: 'Mann-Kendall, Hamed-Rao modified (corrects for year-to-year memory)',
  },
  answerScope: (boxLabel) => `Satellite estimate averaged over the ${boxLabel}, not a rain gauge reading.`,
  pettittStep: (year, p) =>
    `A step change test points to ${year} as the most likely break (p = ${p}).`,
  pettittSensor: 'It coincides with the satellite transition and may be an artifact.',
  pettittNoStep: (year, p) => `A step change test finds no significant break (most likely year ${year}, p = ${p}).`,

  // 4. Annual chart
  chartHeading: 'Rainfall year by year',
  chartIntro: (boxLabel) => `Annual total rainfall over the ${boxLabel}. The line is the estimated trend (Sen's slope).`,
  chartBars: 'Annual total (mm)',
  chartLine: "Trend line (Sen's slope)",
  chartMarker: 'Satellite change (TRMM to GPM)',
  chartMarkerShort: 'Satellite change',
  chartMarkerNote: (year) =>
    `The satellite constellation behind IMERG changed in ${year} (TRMM to GPM). A jump at that point can look like a trend without being one.`,
  chartExcluded: (years) => `Years left out because months are missing: ${years}. They appear as gaps, never filled in.`,
  chartNoExcluded: 'No year is missing data.',
  chartAlt: (verdict, first, last, slope, lo, hi) =>
    `Bar chart of annual rainfall from ${first} to ${last}. ${verdict} Estimated change ${slope} mm per year (95% confidence interval ${lo} to ${hi}).`,
  tooltipTotal: 'Total',
  chartTableToggle: 'Show the yearly numbers',
  chartTableYear: 'Year',
  chartTableTotal: 'Total (mm)',
  chartTableExcluded: 'excluded',
  noBox: 'The headline box is missing from annual.json.',

  // 5. Map
  mapHeading: 'Where: the boxes and an exploratory trend map',
  mapIntro: (boxLabel) =>
    `The answer above uses the highlighted ${boxLabel}. The coloured grid runs the same test on each satellite cell separately.`,
  mapExploratory: (n, fp) => `Exploratory: ${n} separate tests, about ${fp} false positives expected by chance.`,
  mapSignificant: (k) => `${k} cells reach significance on their own. Expect some of those to be chance.`,
  mapNoneSignificant: 'No cell reaches significance on its own.',
  mapUnavailable: 'Trend map not available for this data source.',
  mapLegendDrier: '- Drier',
  mapLegendWetter: '+ Wetter',
  mapLegendNeutral: 'Near zero',
  mapLegendTitle: "Sen's slope, mm per year",
  mapHeadlineBox: 'headline box',
  mapCellTooltip: (slope, p, mean) => `Slope ${slope} mm per year, p = ${p}, mean ${mean} mm per year`,
  mapLoading: 'Loading map...',
  mapA11y: 'Map of the Douala area with the study boxes and the per-cell trend grid. The same numbers are in the robustness table.',

  // 6. Robustness
  robustHeading: 'Does the answer depend on choices?',
  robustIntro:
    'We repeated the test with other box sizes and datasets. These rows only check robustness: the headline is fixed in advance and never swapped.',
  robustCols: ['Box', 'Dataset', 'Years', "Slope (mm/yr)", '95% interval', 'p', 'Result'],
  robustHeadlineTag: 'headline',
  robustEmpty: 'No sensitivity rows in this run.',

  // 7. Explanation
  explainHeading: 'In plain words',
  explainSummary: 'Summary',
  explainMeans: 'What it means',
  explainNotMeans: 'What it does not mean',
  explainTag: {
    template: 'Template text',
    gemini: 'Rewritten by Gemini, numbers checked by code',
  },
  explainChecksFailed: 'Warning: the automatic number and wording checks did not pass for this text.',

  // 8. Limitations (fallback text is used only if explanation.json fails to load)
  limitsHeading: 'Limitations',
  limitsIntro: 'Read these before quoting any number from this page.',
  limitsFallback: [
    'The satellite constellation changed in the middle of the record (TRMM to GPM), which can create artifacts that look like a trend.',
    'IMERG has lower skill near the coast, and Douala sits on the Wouri estuary.',
    'A short record of annual values gives the test low statistical power.',
    'The numbers are a satellite estimate averaged over an area, not a local reading.',
  ],

  // 9. Method and data
  methodHeading: 'Method and data',
  methodText:
    'Monthly mean rain rates are converted to monthly totals, summed into annual totals for each box, then tested for a monotonic trend with Mann-Kendall and Sen\'s slope. The test, box and period were fixed before looking at results.',
  methodDoi: 'Dataset DOI',
  methodAccess: 'Access method',
  methodPeriod: 'Period',
  methodGranules: 'Monthly files used',
  methodCommit: 'Code version',
  methodGenerated: 'Results generated',
  methodRead: 'Read the full method',
  methodRepo: 'Source code on GitHub',
  access: {
    earthaccess: 'NASA Earthdata (earthaccess), full grid',
    giovanni_csv: 'NASA Giovanni, area-averaged series (fallback)',
    mock: 'Synthetic mock data (not NASA data)',
  },

  // 10. Footer
  footerTeam: 'Team',
  team: ['Yann', 'Firmin', 'Theophile', 'Bako', 'Franck', 'Pavel'],
  footerEvent: 'Built for NASA Space Apps 2026',
  challenge: null, // Lead fills in the official challenge name (issue #1)
  footerChallenge: (name) => `Challenge: ${name}`,
  footerData: 'Data: NASA GES DISC. Map tiles: OpenStreetMap contributors.',
}
