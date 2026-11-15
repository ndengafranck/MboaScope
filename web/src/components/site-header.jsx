import { content } from '../content.js'
import { IconCalendar, IconDatabase, IconSatellite } from './icons.jsx'

// Section 1. Hero: the question, the dataset and the period (from provenance.json).
export default function SiteHeader({ provenance }) {
  const p = provenance.data
  return (
    <header className="hero" id="top">
      <div className="hero-bg" aria-hidden="true" />
      <div className="container hero-inner">
        <p className="eyebrow">
          <IconSatellite size={16} /> {content.eyebrow}
        </p>
        <h1>{content.question}</h1>
        <p className="lede">{content.subtitle}</p>
        <ul className="chips" aria-label={content.datasetLabel}>
          {p ? (
            <>
              <li className="chip">
                <IconDatabase size={15} />
                <span>
                  <span className="chip-k">{content.datasetLabel}</span>
                  {content.headerDataset(p.dataset.short_name, p.dataset.version)}
                </span>
              </li>
              <li className="chip">
                <IconCalendar size={15} />
                <span>
                  <span className="chip-k">{content.periodLabel}</span>
                  {content.headerPeriod(p.period.start, p.period.end)}
                </span>
              </li>
            </>
          ) : provenance.status === 'error' ? (
            <li className="chip chip-error">{content.errorFile('provenance')}</li>
          ) : (
            <li className="chip chip-loading" aria-busy="true">
              {content.loading}
            </li>
          )}
        </ul>
      </div>
    </header>
  )
}
