import { content } from '../content.js'
import { VERDICT_CLASS, boxLabel, num, pValue, signed } from '../lib/format.js'
import { SENSOR_CHANGE_YEAR } from '../lib/science.js'
import { IconInfo, IconTrend } from './icons.jsx'
import { Section } from './section.jsx'

// Section 3. The verdict and its numbers, straight from analysis.json.
export default function AnswerCard({ analysis, annual }) {
  return (
    <Section
      id="answer"
      title={content.answerHeading}
      subtitle={content.answerSub}
      icon={IconTrend}
      files={[['analysis', analysis]]}
      className="answer"
    >
      {analysis.data && <AnswerBody h={analysis.data.headline} annual={annual.data} />}
    </Section>
  )
}

// Interval plot: zero, the 95% interval and the point estimate on one axis.
// Only places the three JSON values on a line; computes no statistic.
function IntervalPlot({ lo, hi, est }) {
  if ([lo, hi, est].some((v) => v === null || v === undefined)) return null
  const min = Math.min(lo, 0)
  const max = Math.max(hi, 0)
  const pad = (max - min) * 0.12 || 1
  const a = min - pad
  const b = max + pad
  const x = (v) => `${((v - a) / (b - a)) * 100}%`
  return (
    <div className="interval" aria-hidden="true">
      <div className="interval-track">
        <span className="interval-band" style={{ left: x(lo), width: `calc(${x(hi)} - ${x(lo)})` }} />
        <span className="interval-zero" style={{ left: x(0) }}>
          <span className="interval-zero-label">0</span>
        </span>
        <span className="interval-dot" style={{ left: x(est) }} />
      </div>
      <div className="interval-ends">
        <span style={{ left: x(lo) }}>{signed(lo)}</span>
        <span style={{ left: x(hi) }}>{signed(hi)}</span>
      </div>
    </div>
  )
}

function AnswerBody({ h, annual }) {
  const used = h.mk_test_used === 'hamed_rao' ? h.mk_hamed_rao : h.mk_original
  const [lo, hi] = h.sen_ci95 ?? [null, null]
  const crossesZero = lo !== null && hi !== null && lo <= 0 && hi >= 0
  const pt = h.pettitt
  const tone = VERDICT_CLASS[h.verdict] ?? 'is-neutral'

  return (
    <div className={`answer-grid ${tone}`}>
      <div className="answer-main">
        <p className="verdict-badge">
          <span className="verdict-symbol" aria-hidden="true">
            {content.verdictSymbol[h.verdict] ?? '?'}
          </span>
          {content.verdictShort[h.verdict] ?? content.verdictUnknown}
        </p>
        <p className="verdict">{content.verdict[h.verdict] ?? content.verdictUnknown}</p>

        <div className="slope">
          <p className="kpi-label">{content.slopeLabel}</p>
          <p className="slope-value">
            <span className="big-number">{signed(h.sen_slope_mm_per_year)}</span>
            <span className="slope-unit">{content.slopeUnit}</span>
          </p>
          <IntervalPlot lo={lo} hi={hi} est={h.sen_slope_mm_per_year} />
          <p className="ci">{content.ciText(signed(lo), signed(hi))}</p>
          {crossesZero && <p className="ci-note">{content.ciCrossesZero}</p>}
        </div>
      </div>

      <div className="answer-side">
        <dl className="kpis">
          <div className="kpi">
            <dt className="kpi-label">{content.pctLabel}</dt>
            <dd>
              <span className="kpi-value">{signed(h.pct_per_decade)}</span>
              <span className="kpi-unit">{content.pctUnit}</span>
            </dd>
          </div>
          <div className="kpi">
            <dt className="kpi-label">{content.pLabel}</dt>
            <dd>
              <span className="kpi-value">{pValue(used?.p)}</span>
              <span className="kpi-unit">{content.pHint}</span>
            </dd>
          </div>
          <div className="kpi">
            <dt className="kpi-label">{content.yearsLabel}</dt>
            <dd>
              <span className="kpi-value">{num(h.n_years)}</span>
              <span className="kpi-unit">{h.period}</span>
            </dd>
          </div>
          <div className="kpi">
            <dt className="kpi-label">{content.meanLabel}</dt>
            <dd>
              <span className="kpi-value">{num(h.mean_annual_mm)}</span>
              <span className="kpi-unit">{content.mmPerYear}</span>
            </dd>
          </div>
        </dl>
        <dl className="meta-list">
          <div>
            <dt>{content.testLabel}</dt>
            <dd>{content.tests[h.mk_test_used] ?? h.mk_test_used}</dd>
          </div>
          {pt && (
            <div>
              <dt>{content.pettittLabel}</dt>
              <dd>
                {pt.significant
                  ? content.pettittStep(pt.change_year, pValue(pt.p))
                  : content.pettittNoStep(pt.change_year, pValue(pt.p))}
                {pt.significant && Math.abs(pt.change_year - SENSOR_CHANGE_YEAR) <= 1 && ` ${content.pettittSensor}`}
              </dd>
            </div>
          )}
        </dl>
        <p className="scope">
          <IconInfo size={16} />
          <span>{content.answerScope(boxLabel(annual, h.box))}</span>
        </p>
      </div>
    </div>
  )
}
