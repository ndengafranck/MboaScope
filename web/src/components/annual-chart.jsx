import { Bar, CartesianGrid, ComposedChart, Line, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { content } from '../content.js'
import { boxLabel, firstYear, num, signed } from '../lib/format.js'
import { SENSOR_CHANGE_YEAR } from '../lib/science.js'
import { IconChart } from './icons.jsx'
import { Section } from './section.jsx'

// Section 4. Annual totals of the headline box, the Sen line from analysis.json,
// the 2014 satellite marker and gaps for excluded years.
export default function AnnualChart({ annual, analysis }) {
  return (
    <Section
      id="chart"
      title={content.chartHeading}
      subtitle={annual.data && analysis.data ? content.chartIntro(boxLabel(annual.data, analysis.data.headline.box)) : null}
      icon={IconChart}
      files={[
        ['annual', annual],
        ['analysis', analysis],
      ]}
    >
      {annual.data && analysis.data && <ChartBody annual={annual.data} h={analysis.data.headline} />}
    </Section>
  )
}

function buildRows(box, h) {
  const x0 = firstYear(h.period)
  const byYear = new Map(box.years.map((y) => [y.year, y]))
  for (const y of box.excluded_years ?? []) if (!byYear.has(y)) byYear.set(y, { year: y, complete: false })
  const years = [...byYear.keys()].sort((a, b) => a - b)
  if (years.length === 0) return []
  const rows = []
  for (let year = years[0]; year <= years[years.length - 1]; year++) {
    const y = byYear.get(year)
    const ok = y && y.complete !== false && y.total_mm !== undefined
    rows.push({
      year,
      total: ok ? y.total_mm : null,
      // The contract formula: intercept + slope x (year - first year). No median here.
      trend: x0 === null ? null : h.sen_intercept_mm + h.sen_slope_mm_per_year * (year - x0),
    })
  }
  return rows
}

function ChartBody({ annual, h }) {
  const box = annual.boxes?.[h.box]
  if (!box) return <p className="state state-error">{content.noBox}</p>
  const rows = buildRows(box, h)
  const excluded = rows.filter((r) => r.total === null).map((r) => r.year)
  const [lo, hi] = h.sen_ci95 ?? [null, null]
  const first = rows[0]?.year
  const last = rows[rows.length - 1]?.year
  const alt = content.chartAlt(
    content.verdict[h.verdict] ?? '',
    first,
    last,
    signed(h.sen_slope_mm_per_year),
    signed(lo),
    signed(hi),
  )

  return (
    <figure className="chart">
      <ul className="legend-row" aria-hidden="true">
        <li>
          <span className="key-bar" /> {content.chartBars}
        </li>
        <li>
          <span className="key-line" /> {content.chartLine}
        </li>
        <li>
          <span className="key-marker" /> {content.chartMarker}
        </li>
      </ul>
      <div className="chart-box" role="img" aria-label={alt}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={rows} margin={{ top: 26, right: 8, bottom: 0, left: -6 }}>
            <defs>
              <linearGradient id="barFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--bar-top)" />
                <stop offset="100%" stopColor="var(--bar-bottom)" />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} stroke="var(--grid)" strokeDasharray="3 4" />
            <XAxis
              dataKey="year"
              tick={{ fontSize: 11, fill: 'var(--text-3)', fontFamily: 'var(--mono)' }}
              tickLine={false}
              axisLine={{ stroke: 'var(--border)' }}
              minTickGap={14}
            />
            <YAxis
              tick={{ fontSize: 11, fill: 'var(--text-3)', fontFamily: 'var(--mono)' }}
              tickFormatter={(v) => num(v)}
              tickLine={false}
              axisLine={false}
              width={52}
            />
            <Tooltip content={<ChartTooltip />} cursor={{ fill: 'var(--hover)' }} />
            <Bar dataKey="total" fill="url(#barFill)" radius={[4, 4, 0, 0]} maxBarSize={28} isAnimationActive={false} />
            <Line
              dataKey="trend"
              type="linear"
              stroke="var(--trend)"
              strokeWidth={2.5}
              dot={false}
              activeDot={false}
              isAnimationActive={false}
            />
            <ReferenceLine
              x={SENSOR_CHANGE_YEAR}
              stroke="var(--marker)"
              strokeWidth={2}
              strokeDasharray="5 4"
              label={{
                value: content.chartMarkerShort,
                position: 'top',
                fill: 'var(--marker)',
                fontSize: 11,
                fontWeight: 600,
              }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <figcaption className="chart-notes">
        <p className="note note-marker">
          <span className="key-marker" aria-hidden="true" />
          <span>{content.chartMarkerNote(SENSOR_CHANGE_YEAR)}</span>
        </p>
        <p className="note">
          <span className="key-gap" aria-hidden="true" />
          <span>{excluded.length > 0 ? content.chartExcluded(excluded.join(', ')) : content.chartNoExcluded}</span>
        </p>
        <p className="sr-only">{alt}</p>
      </figcaption>
      <details className="chart-data">
        <summary>{content.chartTableToggle}</summary>
        <table className="data-table">
          <thead>
            <tr>
              <th scope="col">{content.chartTableYear}</th>
              <th scope="col">{content.chartTableTotal}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.year}>
                <td>{r.year}</td>
                <td>{r.total === null ? content.chartTableExcluded : num(r.total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </figure>
  )
}

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const row = payload[0].payload
  return (
    <div className="tooltip">
      <span className="tooltip-year">{label}</span>
      <span className="tooltip-row">
        <span className="key-bar" aria-hidden="true" />
        {content.tooltipTotal}
        <strong>{row.total === null ? content.chartTableExcluded : `${num(row.total)} ${content.mmUnit}`}</strong>
      </span>
    </div>
  )
}
