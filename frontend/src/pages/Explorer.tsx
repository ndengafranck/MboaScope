import { Card } from '../components/common/Card'
import { ErrorMessage, Loading } from '../components/common/Status'
import { RegionMap } from '../components/maps/RegionMap'
import { useApi } from '../hooks/useApi'
import { periodIsValid, useInvestigation } from '../hooks/useInvestigation'
import { api } from '../services/api'

export default function Explorer() {
  const { regions, region, request, setRequest } = useInvestigation()
  const ok = periodIsValid(request) && !!region?.has_data
  const spatial = useApi(() => api.spatial(request), [request.region_id, request.start_year, request.end_year], ok)
  const s = spatial.data

  return (
    <div className="grid">
      <div className="span-8">
        <Card
          title="Study regions"
          subtitle="Click a green dot to choose a region. The green square is the 33 km headline box."
        >
          <RegionMap regions={regions} selected={region} spatial={s} onSelect={(id) => setRequest({ region_id: id })} />
        </Card>
      </div>
      <div className="span-4">
        <Card title="Per-cell trends (exploratory)">
          {spatial.error && <ErrorMessage message={spatial.error} />}
          {spatial.loading && <Loading />}
          {s && !s.available && <p>Per-cell values are not available for this region (area-averaged data only).</p>}
          {s && s.available && (
            <>
              <p>
                <strong>{s.n_significant}</strong> of {s.n_cells} cells show a trend with p &lt; {s.alpha}.
              </p>
              <p className="callout">
                By chance alone about <strong>{s.expected_false_positives}</strong> cells would pass that threshold even
                with no real trend. Outlined cells are below it. Do not read single cells as findings.
              </p>
              <ul className="legend">
                <li>
                  <span className="swatch swatch-wetter" /> wetter (positive Sen slope)
                </li>
                <li>
                  <span className="swatch swatch-drier" /> drier (negative Sen slope)
                </li>
              </ul>
            </>
          )}
          {region && (
            <dl className="facts">
              <dt>Region</dt>
              <dd>
                {region.name}, {region.admin_region}
              </dd>
              <dt>Centre cell</dt>
              <dd>
                {region.centre[0]}° N, {region.centre[1]}° E
              </dd>
              <dt>Coastal</dt>
              <dd>{region.coastal ? 'yes' : 'no'}</dd>
              <dt>Box checked on a map</dt>
              <dd>{region.verified ? 'yes' : 'not yet'}</dd>
            </dl>
          )}
        </Card>
      </div>
    </div>
  )
}
