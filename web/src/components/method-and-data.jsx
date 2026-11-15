import { content } from '../content.js'
import { num } from '../lib/format.js'
import { METHOD_URL, REPO_URL } from '../lib/science.js'
import { IconDatabase, IconExternal, IconGithub } from './icons.jsx'
import { Section } from './section.jsx'

// Section 9. Method summary and provenance: DOI, access method, period, commit.
export default function MethodAndData({ provenance }) {
  const p = provenance.data
  return (
    <Section
      id="method"
      title={content.methodHeading}
      subtitle={content.methodSub}
      icon={IconDatabase}
      files={[['provenance', provenance]]}
    >
      {p && (
        <div className="method-grid">
          <div className="method-text">
            <ol className="steps">
              {content.methodSteps.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
            <p className="muted">{content.methodText}</p>
            <div className="links">
              <a className="btn btn-primary" href={METHOD_URL}>
                {content.methodRead}
                <IconExternal size={15} />
              </a>
              <a className="btn btn-ghost" href={REPO_URL}>
                <IconGithub size={16} />
                {content.methodRepo}
              </a>
            </div>
          </div>
          <dl className="facts">
            <div>
              <dt>{content.methodDoi}</dt>
              <dd>
                <a href={`https://doi.org/${p.dataset.doi}`} className="mono">
                  {p.dataset.doi}
                </a>
                <span className="fact-sub">{p.dataset.name}</span>
              </dd>
            </div>
            <div>
              <dt>{content.methodAccess}</dt>
              <dd>{content.access[p.access_method] ?? p.access_method}</dd>
            </div>
            <div>
              <dt>{content.methodPeriod}</dt>
              <dd className="mono">{content.headerPeriod(p.period.start, p.period.end)}</dd>
            </div>
            <div>
              <dt>{content.methodGranules}</dt>
              <dd className="mono">{num(p.granule_count)}</dd>
            </div>
            <div>
              <dt>{content.methodCommit}</dt>
              <dd>
                {/^[0-9a-f]{7,40}$/.test(p.code_commit) ? (
                  <a href={`${REPO_URL}/commit/${p.code_commit}`} className="mono">
                    {p.code_commit}
                  </a>
                ) : (
                  <span className="mono">{p.code_commit}</span>
                )}
              </dd>
            </div>
            <div>
              <dt>{content.methodGenerated}</dt>
              <dd className="mono">
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
        </div>
      )}
    </Section>
  )
}
