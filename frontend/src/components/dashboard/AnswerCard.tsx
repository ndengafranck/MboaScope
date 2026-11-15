import { pValue, signed, VERDICT_TEXT, VERDICT_TONE } from '../../services/format'
import type { Headline } from '../../types/api'

/** The one question MboaScope answers, for the selected region and period. */
export function AnswerCard({ h }: { h: Headline }) {
  const tone = VERDICT_TONE[h.verdict]
  const p = h.mk_test_used === 'hamed_rao' ? h.mk_hamed_rao.p : h.mk_original.p
  const [lo, hi] = h.sen_ci95
  return (
    <section className={`answer answer-${tone}`} aria-labelledby="answer-title">
      <p className="answer-q">
        Has rainfall changed around {h.region_name}, {h.period}?
      </p>
      <h1 id="answer-title" className="answer-verdict">
        {VERDICT_TEXT[h.verdict]}
      </h1>
      <dl className="answer-stats">
        <div>
          <dt>Estimated change</dt>
          <dd>
            {signed(h.sen_slope_mm_per_year)} <small>mm / year</small>
          </dd>
        </div>
        <div>
          <dt>95% interval</dt>
          <dd>
            {signed(lo)} to {signed(hi)}
          </dd>
        </div>
        <div>
          <dt>Per decade</dt>
          <dd>{signed(h.pct_per_decade)}%</dd>
        </div>
        <div>
          <dt>p-value</dt>
          <dd>
            {pValue(p)} <small>(α = {h.alpha})</small>
          </dd>
        </div>
      </dl>
      <p className="answer-foot">
        {h.n_years} complete years, mean {h.mean_annual_mm.toLocaleString('en-GB')} mm per year, satellite estimate over
        a box of about 33 km.
      </p>
    </section>
  )
}
