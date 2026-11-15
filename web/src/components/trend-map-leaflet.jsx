import 'leaflet/dist/leaflet.css'
import { MapContainer, Rectangle, TileLayer, Tooltip } from 'react-leaflet'
import { content } from '../content.js'
import { num, pValue, signed } from '../lib/format.js'
import { OSM_ATTRIBUTION, OSM_TILES } from '../lib/science.js'

// The Leaflet part of section 5, loaded as its own chunk.
// Colours: brown = drier, blue = wetter, pale near zero. Signs are always
// printed in tooltips and the legend, so colour is never the only signal.

const DRIER = [135, 71, 15]
const WETTER = [29, 92, 150]
const NEUTRAL = [241, 241, 236]

function mix(a, b, t) {
  return `rgb(${a.map((v, i) => Math.round(v + (b[i] - v) * t)).join(',')})`
}

function slopeColor(slope, maxAbs) {
  if (!maxAbs || slope === null || slope === undefined) return `rgb(${NEUTRAL.join(',')})`
  const t = Math.min(Math.abs(slope) / maxAbs, 1)
  return mix(NEUTRAL, slope < 0 ? DRIER : WETTER, t)
}

// Grid spacing from the data itself (smallest gap between cell centres), so no
// cell size is hardcoded here.
function halfStep(cells) {
  const lats = [...new Set(cells.map((c) => c.lat))].sort((a, b) => a - b)
  let step = Infinity
  for (let i = 1; i < lats.length; i++) step = Math.min(step, lats[i] - lats[i - 1])
  return Number.isFinite(step) ? step / 2 : 0.05
}

const toLatLng = ([south, north, west, east]) => [
  [south, west],
  [north, east],
]

export default function TrendMapLeaflet({ s, annual, headlineBox, maxAbs }) {
  const half = halfStep(s.cells)
  const boxes = Object.entries(annual.boxes ?? {})
  const all = s.cells.length
    ? [
        [Math.min(...s.cells.map((c) => c.lat)) - half, Math.min(...s.cells.map((c) => c.lon)) - half],
        [Math.max(...s.cells.map((c) => c.lat)) + half, Math.max(...s.cells.map((c) => c.lon)) + half],
      ]
    : toLatLng(annual.boxes?.[headlineBox]?.bounds ?? [0, 0, 0, 0])
  const coarse = typeof window !== 'undefined' && window.matchMedia?.('(pointer: coarse)').matches

  return (
    <MapContainer
      bounds={all}
      boundsOptions={{ padding: [8, 8] }}
      zoomSnap={0.25}
      scrollWheelZoom={false}
      dragging={!coarse}
      className="leaflet-box"
      attributionControl
    >
      <TileLayer url={OSM_TILES} attribution={OSM_ATTRIBUTION} />
      {s.cells.map((c) => {
        const sig = c.p !== null && c.p < s.alpha
        return (
          <Rectangle
            key={`${c.lat},${c.lon}`}
            bounds={[
              [c.lat - half, c.lon - half],
              [c.lat + half, c.lon + half],
            ]}
            pathOptions={{
              color: sig ? '#0f172a' : '#ffffff',
              weight: sig ? 2 : 0.5,
              fillColor: slopeColor(c.sen_slope_mm_per_year, maxAbs),
              fillOpacity: 0.72,
            }}
          >
            <Tooltip sticky>
              {content.mapCellTooltip(signed(c.sen_slope_mm_per_year), pValue(c.p), num(c.mean_annual_mm))}
            </Tooltip>
          </Rectangle>
        )
      })}
      {boxes.map(([id, b]) => {
        const head = id === headlineBox
        return (
          <Rectangle
            key={id}
            bounds={toLatLng(b.bounds)}
            interactive={false}
            pathOptions={{
              color: head ? '#0f172a' : '#334155',
              weight: head ? 3.5 : 1.5,
              dashArray: head ? null : '6 5',
              fill: false,
            }}
          />
        )
      })}
    </MapContainer>
  )
}
