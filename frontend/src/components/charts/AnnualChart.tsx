import { Bar, CartesianGrid, ComposedChart, Line, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { num, SENSOR_CHANGE_YEAR } from '../../services/format'
import type { AnnualPoint, Headline } from '../../types/api'

interface Row {
  year: number
  total: number | null
  trend: number | null
}

/** Annual totals, the Sen line from the backend, and the 2014 satellite change. */
export function AnnualChart({ years, h, height = 320 }: { years: AnnualPoint[]; h: Headline | null; height?: number }) {
  const first = h ? Number(h.period.split('-')[0]) : null
  const rows: Row[] = years.map((y) => ({
    year: y.year,
    total: y.complete ? y.total_mm : null,
    // Contract formula: intercept + slope x (year - first year). The frontend never fits a line.
    trend: h && first !== null ? h.sen_intercept_mm + h.sen_slope_mm_per_year * (y.year - first) : null,
  }))
  const showMarker = rows.some((r) => r.year === SENSOR_CHANGE_YEAR)

  return (
    <figure className="chart" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={rows} margin={{ top: 20, right: 8, bottom: 0, left: 0 }}>
          <CartesianGrid vertical={false} stroke="var(--grid)" strokeDasharray="3 4" />
          <XAxis dataKey="year" tickLine={false} axisLine={{ stroke: 'var(--border)' }} minTickGap={14} tick={{ fontSize: 11 }} />
          <YAxis tickFormatter={(v: number) => num(v)} tickLine={false} axisLine={false} width={52} tick={{ fontSize: 11 }} />
          <Tooltip
            formatter={(value, name) => [value === null ? 'excluded' : `${num(Math.round(Number(value)))} mm`, name === 'total' ? 'Annual total' : 'Sen trend']}
            labelFormatter={(label) => `Year ${label}`}
          />
          <Bar dataKey="total" fill="var(--bar)" radius={[4, 4, 0, 0]} maxBarSize={26} isAnimationActive={false} />
          {h && <Line dataKey="trend" stroke="var(--trend)" strokeWidth={2.5} dot={false} isAnimationActive={false} />}
          {showMarker && (
            <ReferenceLine
              x={SENSOR_CHANGE_YEAR}
              stroke="var(--marker)"
              strokeDasharray="5 4"
              label={{ value: 'TRMM → GPM', position: 'top', fill: 'var(--marker)', fontSize: 11 }}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </figure>
  )
}
