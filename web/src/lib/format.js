// Display helpers. They never round: the pipeline already rounded every value
// (see docs/CONTRACT.md). They only add signs and thousands separators.

const plain = new Intl.NumberFormat('en-US', { maximumFractionDigits: 6 })

export function num(v) {
  if (v === null || v === undefined || Number.isNaN(v)) return '?'
  return plain.format(v)
}

// "+14.4" or "-4.1": a sign on every non-zero value, so colour is never the only signal.
export function signed(v) {
  if (v === null || v === undefined || Number.isNaN(v)) return '?'
  if (v > 0) return `+${plain.format(v)}`
  return plain.format(v)
}

// p-values arrive with 3 decimals; a value rounded to zero is shown as "< 0.001".
export function pValue(p) {
  if (p === null || p === undefined || Number.isNaN(p)) return '?'
  if (p === 0) return '< 0.001'
  return plain.format(p)
}

// "Douala box, 3 x 3 cells (about 33 km)" from annual.json, or the raw id.
export function boxLabel(annual, boxId) {
  return annual?.boxes?.[boxId]?.label ?? boxId
}

// "2001-2025" -> 2001. The first year of the period, used as x0 of the Sen line.
export function firstYear(period) {
  const m = /^(\d{4})/.exec(String(period ?? ''))
  return m ? Number(m[1]) : null
}

// CSS class per verdict. Colour is never alone: a +, - or ~ symbol is always shown too.
export const VERDICT_CLASS = {
  significant_increase: 'is-wetter',
  significant_decrease: 'is-drier',
  no_significant_trend: 'is-neutral',
}
