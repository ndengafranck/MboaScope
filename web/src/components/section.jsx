import { content } from '../content.js'

// Shared card: icon, title, optional subtitle, and a loading or error state for
// the files it needs. One missing file only affects the cards that use it.
export function Section({ id, title, subtitle, icon: Icon, files = [], children, className = '', aside }) {
  const failed = files.filter(([, f]) => f.status === 'error').map(([name]) => name)
  const loading = files.some(([, f]) => f.status === 'loading')
  return (
    <section id={id} className={`card ${className}`} aria-labelledby={`${id}-title`}>
      <header className="card-head">
        {Icon && (
          <span className="card-icon">
            <Icon />
          </span>
        )}
        <div className="card-titles">
          <h2 id={`${id}-title`}>{title}</h2>
          {subtitle && <p className="card-sub">{subtitle}</p>}
        </div>
        {aside && <div className="card-aside">{aside}</div>}
      </header>
      <div className="card-body">
        {failed.length > 0 ? (
          <div className="state state-error" role="alert">
            {failed.map((name) => (
              <p key={name}>{content.errorFile(name)}</p>
            ))}
          </div>
        ) : loading ? (
          <div className="skeleton" aria-busy="true">
            <span className="sr-only">{content.loading}</span>
            <span className="sk sk-1" />
            <span className="sk sk-2" />
            <span className="sk sk-3" />
          </div>
        ) : (
          children
        )}
      </div>
    </section>
  )
}
