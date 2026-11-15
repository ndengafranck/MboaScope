export function Loading({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="status status-loading" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" /> {label}
    </div>
  )
}

export function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="status status-error" role="alert">
      {message}
    </div>
  )
}
