import { content } from '../content.js'
import { num } from '../lib/format.js'
import { METHOD_URL, REPO_URL } from '../lib/science.js'
import { Section } from './section.jsx'

// Section 9. Method summary and provenance: DOI, access method, period, commit.
export default function MethodAndData({ provenance }) {
  const p = provenance.data
  return (
    <Section id="method" title={content.methodHeading} files={[['provenance', provenance]]}>
      {p && (
        <>
          <p>{content.methodText}</p>
          <dl className="facts">
            <div>
              <dt>{content.methodDoi}</dt>
              <dd>
                <a href={`https://doi.org/${p.dataset.doi}`}>{p.dataset.doi}</a>
                <span className="muted block">{p.dataset.name}</span>
              </dd>
            </div>
            <div>
              <dt>{content.methodAccess}</dt>
              <dd>{content.access[p.access_method] ?? p.access_method}</dd>
            </div>
            <div>
              <dt>{content.methodPeriod}</dt>
              <dd>{content.headerPeriod(p.period.start, p.period.end)}</dd>
            </div>
            <div>
              <dt>{content.methodGranules}</dt>
              <dd>{num(p.granule_count)}</dd>
            </div>
            <div>
              <dt>{content.methodCommit}</dt>
              <dd>
                {/^[0-9a-f]{7,40}$/.test(p.code_commit) ? (
                  <a href={`${REPO_URL}/commit/${p.code_commit}`}>
                    <code>{p.code_commit}</code>
                  </a>
                ) : (
                  <code>{p.code_commit}</code>
                )}
              </dd>
            </div>
            <div>
              <dt>{content.methodGenerated}</dt>
              <dd>
                <time dateTime={p.generated_at}>{p.generated_at}</time>
              </dd>
            </div>
          </dl>
          {p.notes?.length > 0 && (
            <ul className="notes">
              {p.notes.map((n) => (
                <li key={n}>{n}</li>
              ))}
            </ul>
          )}
          <p className="links">
            <a className="button" href={METHOD_URL}>
              {content.methodRead}
            </a>
            <a className="button button-quiet" href={REPO_URL}>
              {content.methodRepo}
            </a>
          </p>
        </>
      )}
    </Section>
  )
}
