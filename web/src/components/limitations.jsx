import { content } from '../content.js'
import { IconAlert } from './icons.jsx'

// Section 8. Always visible, never collapsed. If explanation.json cannot be
// loaded, the fixed threats from docs/SCIENCE.md are shown instead of nothing.
export default function Limitations({ explanation }) {
  const items = explanation.data?.limitations?.length ? explanation.data.limitations : content.limitsFallback
  return (
    <section id="limitations" className="card limitations" aria-labelledby="limitations-title">
      <header className="card-head">
        <span className="card-icon card-icon-warn">
          <IconAlert />
        </span>
        <div className="card-titles">
          <h2 id="limitations-title">{content.limitsHeading}</h2>
          <p className="card-sub">{content.limitsIntro}</p>
        </div>
      </header>
      <div className="card-body">
        <ol className="limits">
          {items.map((text, i) => (
            <li key={text}>
              <span className="limit-n" aria-hidden="true">
                {i + 1}
              </span>
              <span>{text}</span>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}
