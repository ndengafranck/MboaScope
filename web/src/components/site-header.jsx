import { content } from '../content.js'
import { IconCalendar, IconDatabase, IconSatellite } from './icons.jsx'

// Decorative landscape at the bottom of the hero: Mount Cameroon, the hills
// and the Wouri estuary, with a little rain. Purely decorative.
function Landscape() {
  return (
    <svg className="hero-land" viewBox="0 0 1440 220" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">
      <g className="rain" stroke="#cfe3d6" strokeOpacity="0.35" strokeWidth="2" strokeLinecap="round">
        <path d="M1040 20l-8 22M1080 6l-8 22M1120 30l-8 22M1160 12l-8 22M1200 36l-8 22M1240 8l-8 22M1000 40l-8 22" />
      </g>
      <path d="M0 150 L180 118 L300 128 L470 70 L560 40 L610 52 L700 96 L860 120 L1010 104 L1180 130 L1440 110 L1440 220 L0 220Z" fill="#08301f" fillOpacity="0.75" />
      <path d="M0 176 L160 158 L340 170 L520 146 L700 164 L900 150 L1100 168 L1300 154 L1440 162 L1440 220 L0 220Z" fill="#0a3a28" />
      <path
        d="M0 196 C120 186 240 206 360 196 C480 186 600 206 720 196 C840 186 960 206 1080 196 C1200 186 1320 206 1440 196 L1440 220 L0 220Z"
        fill="#fbf6ec"
      />
      <path
        d="M0 188 C120 178 240 198 360 188 C480 178 600 198 720 188 C840 178 960 198 1080 188 C1200 178 1320 198 1440 188"
        fill="none"
        stroke="#7fb3e0"
        strokeOpacity="0.5"
        strokeWidth="2"
      />
    </svg>
  )
}

// Section 1. Hero: the question, the dataset and the period (from provenance.json).
export default function SiteHeader({ provenance }) {
  const p = provenance.data
  const [before, wetter, middle, drier, after] = content.questionParts
  return (
    <header className="hero" id="top">
      <div className="hero-bg" aria-hidden="true" />
      <div className="container hero-inner">
        <p className="eyebrow">
          <span className="eyebrow-star" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="14" height="14">
              <path d="M12 2l2.9 6.9 7.1.6-5.4 4.7 1.7 7-6.3-3.9-6.3 3.9 1.7-7L2 9.5l7.1-.6z" fill="currentColor" />
            </svg>
          </span>
          {content.eyebrow}
        </p>
        <h1>
          {before}
          <span className="word-wetter">{wetter}</span>
          {middle}
          <span className="word-drier">{drier}</span>
          {after}
        </h1>
        <p className="hero-fr" lang="fr">
          {content.questionFr}
        </p>
        <p className="lede">{content.subtitle}</p>
        <ul className="chips" aria-label={content.datasetLabel}>
          <li className="chip">
            <IconSatellite size={15} />
            <span>
              <span className="chip-k">{content.sourceLabel}</span>
              {content.sourceValue}
            </span>
          </li>
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
      <Landscape />
    </header>
  )
}
