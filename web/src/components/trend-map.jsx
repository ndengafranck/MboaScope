import { Suspense, lazy } from 'react'
import { content } from '../content.js'
import { boxLabel, num, signed } from '../lib/format.js'
import { Section } from './section.jsx'

// Leaflet is loaded as its own chunk, only when this section renders.
const TrendMapLeaflet = lazy(() => import('./trend-map-leaflet.jsx'))

// Section 5. The study boxes and the exploratory per-cell trend grid.
// The false-positive label is always shown next to the grid.
export default function TrendMap({ spatial, annual, analysis }) {
  return (
    <Section
      id="map"
      title={content.mapHeading}
      files={[
        ['spatial', spatial],
        ['annual', annual],
      ]}
    >
      {spatial.data && annual.data && (
        <MapBody s={spatial.data} annual={annual.data} headlineBox={analysis.data?.headline?.box ?? 'box_3x3'} />
      )}
    </Section>
  )
}

function MapBody({ s, annual, headlineBox }) {
  const cells = s.available ? (s.cells ?? []) : []
  // Colour scale only: symmetric around zero so brown and blue mean the same everywhere.
  const maxAbs = cells.reduce((m, c) => Math.max(m, Math.abs(c.sen_slope_mm_per_year ?? 0)), 0)
  const boxes = Object.entries(annual.boxes ?? {})

  return (
    <>
      <p className="section-intro">{content.mapIntro(boxLabel(annual, headlineBox))}</p>
      {s.available ? (
        <p className="exploratory" role="note">
          <strong>{content.mapExploratory(num(s.n_cells), num(s.expected_false_positives))}</strong>{' '}
          {s.n_significant > 0 ? content.mapSignificant(num(s.n_significant)) : content.mapNoneSignificant}
        </p>
      ) : (
        <p className="state">{content.mapUnavailable}</p>
      )}

      <figure className="map">
        <div className="map-frame" role="img" aria-label={content.mapA11y}>
          <Suspense fallback={<p className="state map-loading">{content.mapLoading}</p>}>
            <TrendMapLeaflet s={{ ...s, cells }} annual={annual} headlineBox={headlineBox} maxAbs={maxAbs} />
          </Suspense>
        </div>
        <figcaption className="map-key">
          {cells.length > 0 && (
            <div className="legend">
              <p className="legend-title">{content.mapLegendTitle}</p>
              <div className="legend-bar" aria-hidden="true" />
              <div className="legend-ends">
                <span>
                  {content.mapLegendDrier}
                  <span className="legend-num">{signed(-maxAbs)}</span>
                </span>
                <span className="center">{content.mapLegendNeutral}</span>
                <span className="right">
                  {content.mapLegendWetter}
                  <span className="legend-num">{signed(maxAbs)}</span>
                </span>
              </div>
              <p className="legend-sig">
                <span className="swatch-sig" aria-hidden="true" /> {content.mapLegendSignificant}
              </p>
            </div>
          )}
          <ul className="box-key">
            {boxes.map(([id, b]) => (
              <li key={id} className={id === headlineBox ? 'is-headline' : ''}>
                <span className="swatch-box" aria-hidden="true" />
                {b.label}
                {id === headlineBox && <span className="pill">{content.mapHeadlineBox}</span>}
              </li>
            ))}
          </ul>
        </figcaption>
      </figure>
    </>
  )
}
