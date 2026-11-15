import { useEffect, useState } from 'react'

export interface ApiState<T> {
  data: T | null
  error: string | null
  loading: boolean
}

/** Run an API call whenever `deps` change; ignore answers that arrive after a newer request. */
export function useApi<T>(fn: () => Promise<T>, deps: unknown[], enabled = true): ApiState<T> {
  const [state, setState] = useState<ApiState<T>>({ data: null, error: null, loading: enabled })

  useEffect(() => {
    if (!enabled) {
      setState({ data: null, error: null, loading: false })
      return
    }
    let current = true
    setState((s) => ({ ...s, loading: true, error: null }))
    fn()
      .then((data) => current && setState({ data, error: null, loading: false }))
      .catch((err: Error) => current && setState({ data: null, error: err.message, loading: false }))
    return () => {
      current = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, ...deps])

  return state
}
