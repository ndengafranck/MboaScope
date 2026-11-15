import { content } from '../content.js'
import { VERDICT_CLASS, boxLabel, num, pValue, signed } from '../lib/format.js'
import { SENSOR_CHANGE_YEAR } from '../lib/science.js'
import { Section } from './section.jsx'

// Section 3. The verdict and its numbers, straight from analysis.json.
export default function AnswerCard({ analysis, annual }) {
  return (
    <Section id="answer" title={content.answerHeading} files={[['analysis', analysis]]} className="answer">
      {analysis.data && <AnswerBody h={analysis.data.headline} annual={annual.data} />}
    </Section>
  )
}

function AnswerBody({ h, annual }) {
  const used = h.mk_test_used === 'hamed_rao' ? h.mk_hamed_rao : h.mk_original
  const [lo, hi] = h.sen_ci95 ?? [null, null]
  const crossesZero = lo !== null && hi !== null && lo <= 0 && hi >= 0
  const pt = h.pettitt

  return (
    <div className={`answer-card ${VERDICT_CLASS[h.verdict] ?? 'is-neutral'}`}>
      <p className="verdict">
        <span className="verdict-symbol" aria-hidden="true">
          {content.verdictSymbol[h.verdict] ?? '?'}
        </span>
        <span>{content.verdict[h.verdict] ?? content.verdictUnknown}</span>
      </p>

      <div className="slope">
        <p className="slope-label">{content.slopeLabel}</p>
        <p className="slope-value">
          <span className="big-number">{signed(h.sen_slope_mm_per_year)}</span>
          <span className="unit">{content.slopeUnit}</span>
        </p>
        <p className="ci">{content.ciText(signed(lo), signed(hi))}</p>
        {crossesZero && <p className="ci-note">{content.ciCrossesZero}</p>}
      </div>

      <dl className="stats-grid">
        <div>
          <dt>{content.pctLabel}</dt>
          <dd>
            {signed(h.pct_per_decade)}
            <span className="unit">{content.pctUnit}</span>
          </dd>
        </div>
        <div>
          <dt>{content.pLabel}</dt>
          <dd>{pValue(used?.p)}</dd>
        </div>
        <div>
          <dt>{content.yearsLabel}</dt>
          <dd>
            {num(h.n_years)}
            <span className="unit">{h.period}</span>
          </dd>
        </div>
        <div>
          <dt>{content.meanLabel}</dt>
          <dd>
            {num(h.mean_annual_mm)}
            <span className="unit">{content.mmUnit}</span>
          </dd>
        </div>
        <div className="wide">
          <dt>{content.testLabel}</dt>
          <dd className="small">{content.tests[h.mk_test_used] ?? h.mk_test_used}</dd>
        </div>
      </dl>

      {pt && (
        <p className="pettitt">
          {pt.significant
            ? content.pettittStep(pt.change_year, pValue(pt.p))
            : content.pettittNoStep(pt.change_year, pValue(pt.p))}
          {pt.significant && Math.abs(pt.change_year - SENSOR_CHANGE_YEAR) <= 1 && ` ${content.pettittSensor}`}
        </p>
      )}
      <p className="scope">{content.answerScope(boxLabel(annual, h.box))}</p>
    </div>
  )
}
