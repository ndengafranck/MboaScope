import { content } from '../content.js'
import { boxLabel, num } from '../lib/format.js'
import { Section } from './section.jsx'

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
    </>
  )
}
