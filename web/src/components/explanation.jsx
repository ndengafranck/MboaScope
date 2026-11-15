import { content } from '../content.js'
import { IconSparkle, IconText } from './icons.jsx'
import { Section } from './section.jsx'

// Section 7. The plain-language fields of explanation.json, tagged by source.
export default function Explanation({ explanation }) {
  const e = explanation.data
  return (
    <Section
      id="explanation"
      title={content.explainHeading}
      subtitle={content.explainSub}
      icon={IconText}
      files={[['explanation', explanation]]}
      aside={
        e && (
          <span className={`badge ${e.source === 'gemini' ? 'badge-ai' : ''}`}>
            {e.source === 'gemini' && <IconSparkle size={13} />}
            {content.explainTag[e.source] ?? e.source}
          </span>
        )
      }
    >
      {e && (
        <div className="explain">
          {e.checks_passed === false && (
            <p className="state state-error" role="alert">
              {content.explainChecksFailed}
            </p>
          )}
          <p className="explain-summary">{e.summary}</p>
          <div className="explain-cols">
            <div className="explain-block">
              <h3>{content.explainMeans}</h3>
              <p>{e.what_it_means}</p>
            </div>
            <div className="explain-block is-not">
              <h3>{content.explainNotMeans}</h3>
              <p>{e.what_it_does_not_mean}</p>
            </div>
          </div>
        </div>
      )}
    </Section>
  )
}
