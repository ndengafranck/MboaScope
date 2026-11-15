// Fetches the five web files from BASE_URL/data/. Each file has its own
// loading / error state, so one missing file never blanks the whole page.
import { useEffect, useState } from 'react'

export const FILES = ['annual', 'analysis', 'spatial', 'explanation', 'provenance']

const initial = Object.fromEntries(FILES.map((name) => [name, { status: 'loading', data: null, error: null }]))

export function useData() {
  const [files, setFiles] = useState(initial)

  useEffect(() => {
    const base = `${import.meta.env.BASE_URL}data/`
    let alive = true
    for (const name of FILES) {
      fetch(`${base}${name}.json`, { cache: 'no-cache' })
        .then((r) => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`)
          return r.json()
        })
        .then((data) => {
          if (alive) setFiles((prev) => ({ ...prev, [name]: { status: 'ready', data, error: null } }))
        })
        .catch((e) => {
          if (alive) setFiles((prev) => ({ ...prev, [name]: { status: 'error', data: null, error: e.message } }))
        })
    }
    return () => {
      alive = false
    }
  }, [])

  // One flag for the banner: true as soon as any loaded file says it is mock.
  const isMock = FILES.some((name) => files[name].data?.is_mock === true)
  return { files, isMock }
}
