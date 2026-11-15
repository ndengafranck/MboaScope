import { Link, useLocation } from 'react-router-dom'
import { AnnualChart } from '../components/charts/AnnualChart'
import { Card } from '../components/common/Card'
import { ErrorMessage, Loading } from '../components/common/Status'
import { AnswerCard } from '../components/dashboard/AnswerCard'
import { useApi } from '../hooks/useApi'
import { periodIsValid, useInvestigation } from '../hooks/useInvestigation'
import { api } from '../services/api'
import { CAVEAT_TITLE } from '../services/format'

export default function Dashboard() {
  const { request } = useInvestigation()
  const { search } = useLocation()
  const ok = periodIsValid(request)
  const key = [request.region_id, request.start_year, request.end_year]
  const trends = useApi(() => api.trends(request), key, ok)
  const series = useApi(() => api.rainfallSeries(request), key, ok)

  if (!ok) return null
  if (trends.error) return <ErrorMessage message={trends.error} />
  if (trends.loading || !trends.data) return <Loading label="Running the trend tests…" />
  const h = trends.data.headline

  return (
    <div className="grid">
      <div className="span-12">
        <AnswerCard h={h} />
      </div>
      <div className="span-8">
        <Card title="Annual rainfall" subtitle="Bars: annual totals. Line: Sen trend. Dashed: 2014 satellite change.">
          {series.data ? <AnnualChart years={series.data.years} h={h} height={280} /> : <Loading />}
        </Card>
      </div>
      <div className="span-4">
        <Card title="Read this before quoting">
          <ul className="caveats">
            {h.caveats.map((c) => (
              <li key={c}>{CAVEAT_TITLE[c] ?? c}</li>
            ))}
          </ul>
          <p className="muted">
            The <Link to={{ pathname: '/assistant', search }}>Assistant</Link> explains each one in plain language.
          </p>
        </Card>
      </div>
      <div className="span-12 next-steps">
        <Link className="tile" to={{ pathname: '/explorer', search }}>
          <strong>Explorer</strong>
          <span>See the study area on the map and the exploratory per-cell trends.</span>
        </Link>
        <Link className="tile" to={{ pathname: '/analysis', search }}>
          <strong>Analysis</strong>
          <span>All test results, the seasonal cycle and robustness checks.</span>
        </Link>
        <Link className="tile" to={{ pathname: '/assistant', search }}>
          <strong>Assistant</strong>
          <span>What the result means, what it does not mean, and what to test next.</span>
        </Link>
      </div>
    </div>
  )
}
