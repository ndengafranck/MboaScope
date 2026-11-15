import { content } from '../content.js'
import { Section } from './section.jsx'

// Section 7. The plain-language fields of explanation.json, tagged by source.
export default function Explanation({ explanation }) {
  const e = explanation.data
  return (
    <Section id="explanation" title={content.explainHeading} files={[['explanation', explanation]]}>
      {e && (
        <div className="explain">
          <p className={`tag ${e.source === 'gemini' ? 'tag-ai' : ''}`}>{content.explainTag[e.source] ?? e.source}</p>
          {e.checks_passed === false && (
            <p className="state state-error" role="alert">
              {content.explainChecksFailed}
            </p>
          )}
          <h3>{content.explainSummary}</h3>
          <p className="explain-summary">{e.summary}</p>
          <h3>{content.explainMeans}</h3>
          <p>{e.what_it_means}</p>
          <h3>{content.explainNotMeans}</h3>
          <p>{e.what_it_does_not_mean}</p>
        </div>
      )}
    </Section>
  )
}
