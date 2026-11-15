import { content } from '../content.js'

// Shared wrapper: a titled section with a loading or error state for the files it needs.
export function Section({ id, title, files = [], children, className = '' }) {
  const failed = files.filter(([, f]) => f.status === 'error').map(([name]) => name)
  const loading = files.some(([, f]) => f.status === 'loading')
  return (
    <section id={id} className={`section ${className}`} aria-labelledby={`${id}-title`}>
      <h2 id={`${id}-title`}>{title}</h2>
      {failed.length > 0 ? (
        <div className="state state-error" role="alert">
          {failed.map((name) => (
            <p key={name}>{content.errorFile(name)}</p>
          ))}
        </div>
      ) : loading ? (
        <p className="state" aria-busy="true">
          {content.loading}
        </p>
      ) : (
        children
      )}
    </section>
  )
}
