// Display helpers only. Rounding is done by the backend; these just print.
import type { Verdict } from '../types/api'

const nf = new Intl.NumberFormat('en-GB')

export const num = (x: number | null | undefined): string => (x === null || x === undefined ? '–' : nf.format(x))

export const signed = (x: number): string => (x > 0 ? `+${nf.format(x)}` : x < 0 ? `−${nf.format(Math.abs(x))}` : '0')

export const pValue = (p: number): string => (p < 0.001 ? '< 0.001' : p.toFixed(3))

export const VERDICT_TEXT: Record<Verdict, string> = {
  significant_increase: 'Statistically significant increase',
  significant_decrease: 'Statistically significant decrease',
  no_significant_trend: 'No statistically significant trend',
}

export const VERDICT_TONE: Record<Verdict, 'wetter' | 'drier' | 'neutral'> = {
  significant_increase: 'wetter',
  significant_decrease: 'drier',
  no_significant_trend: 'neutral',
}

export const CAVEAT_TITLE: Record<string, string> = {
  sensor_change_2014: 'Satellite change in 2014',
  coastal_skill: 'Coastal location',
  short_record: 'Short record',
  area_estimate: 'Area estimate, not a station',
}

export const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

export const SENSOR_CHANGE_YEAR = 2014
