import { useState } from 'react'
import { Card } from '../components/common/Card'
import { ErrorMessage, Loading } from '../components/common/Status'
import { useApi } from '../hooks/useApi'
import { periodIsValid, useInvestigation } from '../hooks/useInvestigation'
import { api } from '../services/api'
import { CAVEAT_TITLE } from '../services/format'

export default function Assistant() {
  const { request, setRequest, regions } = useInvestigation()
  const [useLlm, setUseLlm] = useState(false)
  const ok = periodIsValid(request)
  const res = useApi(
    () => api.interpret({ ...request, use_llm: useLlm }),
    [request.region_id, request.start_year, request.end_year, useLlm],
    ok,
  )
  const trends = useApi(() => api.trends(request), [request.region_id, request.start_year, request.end_year], ok)

  if (!ok) return null
  const e = res.data?.explanation
  const caveats = trends.data?.headline.caveats ?? []

  return (
    <div className="grid">
      <div className="span-8">
        <Card
          title="What the result says"
          subtitle="Written only from the computed statistics. Every number and claim is checked before it is shown."
          action={
            <label className="toggle">
              <input type="checkbox" checked={useLlm} onChange={(ev) => setUseLlm(ev.target.checked)} />
              Plain-language rewrite (Gemini)
            </label>
          }
        >
          {res.error && <ErrorMessage message={res.error} />}
          {res.loading && <Loading label={useLlm ? 'Asking Gemini, then checking its answer…' : 'Writing the explanation…'} />}
          {e && !e.checks_passed && <ErrorMessage message="The explanation failed its checks and is hidden." />}
          {e && e.checks_passed && !res.loading && (
            <article className="explanation">
              <p className="lead">{e.summary}</p>
              <h3>What it means</h3>
              <p>{e.what_it_means}</p>
              <h3>What it does not mean</h3>
              <p>{e.what_it_does_not_mean}</p>
              <h3>Limitations</h3>
              <ul>
                {e.limitations.map((l, i) => (
                  <li key={l}>
                    <strong>{CAVEAT_TITLE[caveats[i]] ?? 'Limitation'}.</strong> {l}
                  </li>
                ))}
              </ul>
              <p className="muted">
                Source: {e.source === 'gemini' ? `Gemini (${e.model}), checked` : 'template'}
                {res.data?.notes.length ? ` · Gemini not used: ${res.data.notes.join('; ')}` : ''}
              </p>
            </article>
          )}
        </Card>
      </div>
      <div className="span-4">
        <Card title="Investigate next">
          {res.data?.suggestions.map((s) => (
            <div key={s.title} className="suggestion">
              <strong>{s.title}</strong>
              <p>{s.reason}</p>
              {s.region_id ? (
                <button
                  type="button"
                  onClick={() => setRequest({ region_id: s.region_id!, start_year: s.start_year, end_year: s.end_year })}
                >
                  Run {s.start_year}–{s.end_year}
                </button>
              ) : (
                <select
                  aria-label="Compare with region"
                  defaultValue=""
                  onChange={(ev) => ev.target.value && setRequest({ region_id: ev.target.value })}
                >
                  <option value="" disabled>
                    Choose a region…
                  </option>
                  {regions
                    .filter((r) => r.has_data && r.id !== request.region_id)
                    .map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.name}
                      </option>
                    ))}
                </select>
              )}
            </div>
          ))}
        </Card>
      </div>
    </div>
  )
}
