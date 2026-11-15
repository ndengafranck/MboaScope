import { content } from '../content.js'

// Section 8. Always visible, never collapsed. If explanation.json cannot be
// loaded, the fixed threats from docs/SCIENCE.md are shown instead of nothing.
export default function Limitations({ explanation }) {
  const items = explanation.data?.limitations?.length ? explanation.data.limitations : content.limitsFallback
  return (
    <section id="limitations" className="section limitations" aria-labelledby="limitations-title">
      <h2 id="limitations-title">{content.limitsHeading}</h2>
      <p className="section-intro">{content.limitsIntro}</p>
      <ol className="limits">
        {items.map((text) => (
          <li key={text}>{text}</li>
        ))}
      </ol>
    </section>
  )
}
