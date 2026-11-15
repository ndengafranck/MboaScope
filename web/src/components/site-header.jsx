import { content } from '../content.js'

// Section 1. Name, question, dataset and period (from provenance.json).
export default function SiteHeader({ provenance }) {
  const p = provenance.data
  return (
    <header className="site-header">
      <div className="wrap">
        <p className="brand">
          <span className="brand-mark" aria-hidden="true" />
          {content.title}
        </p>
        <h1>{content.question}</h1>
        <p className="lede">{content.subtitle}</p>
        {p && (
          <dl className="header-meta">
            <div>
              <dt>{content.datasetLabel}</dt>
              <dd>{content.headerDataset(p.dataset.short_name, p.dataset.version)}</dd>
            </div>
            <div>
              <dt>{content.periodLabel}</dt>
              <dd>{content.headerPeriod(p.period.start, p.period.end)}</dd>
            </div>
          </dl>
        )}
        {provenance.status === 'error' && <p className="state state-error">{content.errorFile('provenance')}</p>}
      </div>
    </header>
  )
}
