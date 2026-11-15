import { AnnualChart } from '../components/charts/AnnualChart'
import { ClimatologyChart } from '../components/charts/ClimatologyChart'
import { Card } from '../components/common/Card'
import { ErrorMessage, Loading } from '../components/common/Status'
import { useApi } from '../hooks/useApi'
import { periodIsValid, useInvestigation } from '../hooks/useInvestigation'
import { api } from '../services/api'
import { pValue, signed, VERDICT_TEXT } from '../services/format'

export default function Analysis() {
  const { request } = useInvestigation()
  const ok = periodIsValid(request)
  const key = [request.region_id, request.start_year, request.end_year]
  const trends = useApi(() => api.trends(request), key, ok)
  const series = useApi(() => api.rainfallSeries(request), key, ok)
  const history = useApi(() => api.history(8), [trends.data?.investigation_id], !!trends.data)

  if (!ok) return null
  if (trends.error) return <ErrorMessage message={trends.error} />
  if (!trends.data || !series.data) return <Loading label="Loading the analysis…" />
  const h = trends.data.headline
  const sd = series.data

  return (
    <div className="grid">
      <div className="span-12">
        <Card title={`Annual rainfall, ${sd.box_label}`} subtitle={`${h.dataset}, ${h.period}`}>
          <AnnualChart years={sd.years} h={h} />
          {sd.excluded_years.length > 0 && (
            <p className="muted">Excluded (fewer than 12 months): {sd.excluded_years.join(', ')}</p>
          )}
          {sd.warnings.map((w) => (
            <p key={w} className="status status-error">
              {w}
            </p>
          ))}
        </Card>
      </div>

      <div className="span-6">
        <Card title="Test results" subtitle={`Primary test: ${h.mk_test_used === 'hamed_rao' ? 'Hamed-Rao modified Mann-Kendall' : 'Mann-Kendall'}`}>
          <table className="table">
            <tbody>
              <tr><th>Verdict</th><td>{VERDICT_TEXT[h.verdict]}</td></tr>
              <tr><th>Mann-Kendall (original)</th><td>τ = {h.mk_original.tau}, z = {h.mk_original.z}, p = {pValue(h.mk_original.p)}</td></tr>
              <tr><th>Hamed-Rao modified</th><td>z = {h.mk_hamed_rao.z}, p = {pValue(h.mk_hamed_rao.p)}</td></tr>
              <tr><th>Lag-1 autocorrelation</th><td>{h.lag1_autocorr} {h.autocorr_significant ? '(significant)' : '(not significant)'}</td></tr>
              <tr><th>Sen's slope</th><td>{signed(h.sen_slope_mm_per_year)} mm/yr (95% CI {signed(h.sen_ci95[0])} to {signed(h.sen_ci95[1])})</td></tr>
              <tr><th>Relative change</th><td>{signed(h.pct_per_decade)}% per decade</td></tr>
              <tr><th>Pettitt change point</th><td>{h.pettitt.change_year}, p = {pValue(h.pettitt.p)} {h.pettitt.significant ? '(significant)' : '(not significant)'}</td></tr>
              <tr><th>Mean annual total</th><td>{h.mean_annual_mm.toLocaleString('en-GB')} mm ({h.n_years} years)</td></tr>
            </tbody>
          </table>
        </Card>
      </div>

      <div className="span-6">
        <Card title="Seasonal cycle" subtitle="Mean monthly total over the selected years">
          <ClimatologyChart data={sd.climatology} />
        </Card>
      </div>

      <div className="span-6">
        <Card title="Robustness checks" subtitle="Same test on smaller and larger boxes. Never promoted to the headline.">
          {trends.data.sensitivity.length === 0 ? (
            <p className="muted">Not available for this data source.</p>
          ) : (
            <table className="table">
              <thead>
                <tr><th>Box</th><th>Slope (mm/yr)</th><th>95% CI</th><th>p</th><th>Verdict</th></tr>
              </thead>
              <tbody>
                {trends.data.sensitivity.map((r) => (
                  <tr key={r.box + r.dataset}>
                    <td>{r.box.replace('box_', '')}</td>
                    <td>{signed(r.sen_slope_mm_per_year)}</td>
                    <td>{signed(r.sen_ci95[0])} to {signed(r.sen_ci95[1])}</td>
                    <td>{pValue(r.p)}</td>
                    <td>{VERDICT_TEXT[r.verdict].replace('Statistically significant', 'Significant')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Card>
      </div>

      <div className="span-6">
        <Card title="Data and provenance">
          <dl className="facts">
            <dt>Dataset</dt><dd>{sd.provenance.dataset}</dd>
            <dt>DOI</dt><dd><a href={`https://doi.org/${sd.provenance.doi}`}>{sd.provenance.doi}</a></dd>
            <dt>Access</dt><dd>{sd.provenance.access_method}</dd>
            <dt>Source units</dt><dd>{sd.provenance.source_units}</dd>
            <dt>Available</dt><dd>{sd.provenance.period.join(' to ')}</dd>
          </dl>
          {sd.provenance.notes.map((n) => <p key={n} className="muted">{n}</p>)}
          {history.data && history.data.length > 0 && (
            <>
              <h3>Recent investigations</h3>
              <ul className="history">
                {history.data.map((i) => (
                  <li key={i.id}>
                    {i.region_id} {i.start_year}–{i.end_year}: {VERDICT_TEXT[i.verdict].toLowerCase()}
                  </li>
                ))}
              </ul>
            </>
          )}
        </Card>
      </div>
    </div>
  )
}
