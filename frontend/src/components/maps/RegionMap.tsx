import 'leaflet/dist/leaflet.css'
import { CircleMarker, MapContainer, Rectangle, TileLayer, Tooltip, useMap } from 'react-leaflet'
import { useEffect } from 'react'
import type { Bounds, Region, SpatialResponse } from '../../types/api'

const CAMEROON_CENTRE: [number, number] = [6.5, 12.5]
const HALF_CELL = 0.05

const toLatLng = (b: Bounds): [[number, number], [number, number]] => [
  [b[0], b[2]],
  [b[1], b[3]],
]

/** Colour a cell by its Sen slope: brown drier, blue wetter. Exploratory only. */
function cellColour(slope: number, maxAbs: number): string {
  const t = Math.min(Math.abs(slope) / (maxAbs || 1), 1)
  const alpha = 0.15 + 0.6 * t
  return slope >= 0 ? `rgba(31, 79, 143, ${alpha})` : `rgba(138, 72, 16, ${alpha})`
}

function FlyTo({ region }: { region: Region | null }) {
  const map = useMap()
  useEffect(() => {
    if (region) map.flyToBounds(toLatLng(region.grid_bounds), { padding: [24, 24], duration: 0.8 })
  }, [map, region])
  return null
}

export function RegionMap({
  regions,
  selected,
  spatial,
  onSelect,
}: {
  regions: Region[]
  selected: Region | null
  spatial: SpatialResponse | null
  onSelect: (id: string) => void
}) {
  const cells = spatial?.available ? spatial.cells : []
  const maxAbs = Math.max(0, ...cells.map((c) => Math.abs(c.sen_slope_mm_per_year)))

  return (
    <div className="map">
      <MapContainer center={CAMEROON_CENTRE} zoom={6} scrollWheelZoom={false} style={{ height: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FlyTo region={selected} />
        {cells.map((c) => (
          <Rectangle
            key={`${c.lat},${c.lon}`}
            bounds={[
              [c.lat - HALF_CELL, c.lon - HALF_CELL],
              [c.lat + HALF_CELL, c.lon + HALF_CELL],
            ]}
            pathOptions={{
              stroke: c.p < (spatial?.alpha ?? 0.05),
              color: '#1c2b23',
              weight: 1.5,
              fillColor: cellColour(c.sen_slope_mm_per_year, maxAbs),
              fillOpacity: 1,
            }}
          >
            <Tooltip>
              {c.sen_slope_mm_per_year > 0 ? '+' : ''}
              {c.sen_slope_mm_per_year} mm/yr · p = {c.p.toFixed(3)} · mean {c.mean_annual_mm} mm
            </Tooltip>
          </Rectangle>
        ))}
        {selected && (
          <Rectangle bounds={toLatLng(selected.boxes.box_3x3.bounds)} pathOptions={{ color: '#0a6a4a', weight: 3, fill: false }}>
            <Tooltip sticky>{selected.boxes.box_3x3.label} (headline box)</Tooltip>
          </Rectangle>
        )}
        {regions.map((r) => (
          <CircleMarker
            key={r.id}
            center={r.centre}
            radius={r.id === selected?.id ? 9 : 6}
            pathOptions={{
              color: '#fffdf8',
              weight: 2,
              fillColor: r.has_data ? '#0a6a4a' : '#9aa59c',
              fillOpacity: 1,
            }}
            eventHandlers={{ click: () => r.has_data && onSelect(r.id) }}
          >
            <Tooltip>
              {r.name} · {r.admin_region}
              {r.has_data ? '' : ' (no data yet)'}
            </Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  )
}
