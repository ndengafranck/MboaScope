import { content } from '../content.js'
import { VERDICT_CLASS, boxLabel, num, pValue, signed } from '../lib/format.js'
import { IconLayers } from './icons.jsx'
import { Section } from './section.jsx'

// Section 6. The headline row first, then the sensitivity rows from analysis.json.
export default function RobustnessTable({ analysis, annual }) {
  return (
    <Section
      id="robustness"
      title={content.robustHeading}
      subtitle={content.robustIntro}
      icon={IconLayers}
      files={[['analysis', analysis]]}
    >
      {analysis.data && <TableBody a={analysis.data} annual={annual.data} />}
    </Section>
  )
}

function TableBody({ a, annual }) {
  const h = a.headline
  const used = h.mk_test_used === 'hamed_rao' ? h.mk_hamed_rao : h.mk_original
  const rows = [
    {
      key: 'headline',
      headline: true,
      box: h.box,
      dataset: h.dataset,
      n_years: h.n_years,
      sen_slope_mm_per_year: h.sen_slope_mm_per_year,
      sen_ci95: h.sen_ci95,
      p: used?.p,
      verdict: h.verdict,
    },
    ...(a.sensitivity ?? []).map((r, i) => ({ key: `s${i}`, ...r })),
  ]
  const [cBox, cData, cYears, cSlope, cCi, cP, cRes] = content.robustCols

  return (
    <>
      <div className="table-scroll" tabIndex={0} role="region" aria-labelledby="robustness-title">
        <table className="robust">
          <thead>
            <tr>
              <th scope="col">{cBox}</th>
              <th scope="col">{cData}</th>
              <th scope="col" className="num">{cYears}</th>
              <th scope="col" className="num">{cSlope}</th>
              <th scope="col" className="num">{cCi}</th>
              <th scope="col" className="num">{cP}</th>
              <th scope="col">{cRes}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.key} className={r.headline ? 'is-headline' : ''}>
                <th scope="row">
                  {boxLabel(annual, r.box)}
                  {r.headline && <span className="pill">{content.robustHeadlineTag}</span>}
                </th>
                <td data-label={cData}>{r.dataset}</td>
                <td className="num" data-label={cYears}>{num(r.n_years)}</td>
                <td className="num" data-label={cSlope}>{signed(r.sen_slope_mm_per_year)}</td>
                <td className="num nowrap" data-label={cCi}>
                  {signed(r.sen_ci95?.[0])} to {signed(r.sen_ci95?.[1])}
                </td>
                <td className="num" data-label={cP}>{pValue(r.p)}</td>
                <td className="result" data-label={cRes}>
                  <span className={`verdict-chip ${VERDICT_CLASS[r.verdict] ?? 'is-neutral'}`}>
                    <span aria-hidden="true">{content.verdictSymbol[r.verdict] ?? '?'}</span>{' '}
                    {content.verdictShort[r.verdict] ?? r.verdict}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rows.length === 1 && <p className="muted">{content.robustEmpty}</p>}
    </>
  )
}
