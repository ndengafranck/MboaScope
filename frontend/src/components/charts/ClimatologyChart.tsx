import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { MONTHS, num } from '../../services/format'
import type { ClimatologyPoint } from '../../types/api'

/** Mean monthly rainfall over the selected years: the seasonal cycle. */
export function ClimatologyChart({ data }: { data: ClimatologyPoint[] }) {
  const rows = data.map((d) => ({ month: MONTHS[d.month - 1], mm: d.mean_mm }))
  return (
    <figure className="chart" style={{ height: 240 }}>
      <ResponsiveContainer width="99%" height="100%">
        <BarChart data={rows} margin={{ top: 10, right: 8, bottom: 0, left: 0 }}>
          <CartesianGrid vertical={false} stroke="var(--grid)" strokeDasharray="3 4" />
          <XAxis dataKey="month" tickLine={false} tick={{ fontSize: 11 }} />
          <YAxis tickFormatter={(v: number) => num(v)} tickLine={false} axisLine={false} width={44} tick={{ fontSize: 11 }} />
          <Tooltip formatter={(v) => [`${num(Number(v))} mm`, 'Mean monthly total']} />
          <Bar dataKey="mm" fill="var(--bar-soft)" radius={[4, 4, 0, 0]} isAnimationActive={false} />
        </BarChart>
      </ResponsiveContainer>
    </figure>
  )
}
