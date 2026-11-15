import type { ReactNode } from 'react'

export function Card({ title, subtitle, children, action, id }: {
  title?: string
  subtitle?: ReactNode
  children: ReactNode
  action?: ReactNode
  id?: string
}) {
  return (
    <section className="card" id={id} aria-labelledby={id && title ? `${id}-title` : undefined}>
      {(title || action) && (
        <header className="card-head">
          <div>
            {title && <h2 id={id ? `${id}-title` : undefined}>{title}</h2>}
            {subtitle && <p className="card-sub">{subtitle}</p>}
          </div>
          {action}
        </header>
      )}
      <div className="card-body">{children}</div>
    </section>
  )
}
