import { useEffect, useState } from 'react'
import { content } from './content.js'

const FILES = ['annual', 'analysis', 'spatial', 'explanation', 'provenance']

export default function App() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const base = `${import.meta.env.BASE_URL}data/`
    Promise.all(
      FILES.map((name) =>
        fetch(`${base}${name}.json`).then((r) => {
          if (!r.ok) throw new Error(`${content.errorPrefix} ${name}.json`)
          return r.json()
        }),
      ),
    )
      .then((list) => setData(Object.fromEntries(FILES.map((n, i) => [n, list[i]]))))
      .catch((e) => setError(e.message))
  }, [])

  if (error) return <main role="alert">{error}</main>
  if (!data) return <main>{content.loading}</main>

  const isMock = Object.values(data).some((d) => d.is_mock)
  const headline = data.analysis.headline

  return (
    <>
      {isMock && <div className="mock-banner">{content.mockBanner}</div>}
      <main>
        <h1>{content.title}</h1>
        <p>
          {headline.verdict} ({headline.period})
        </p>
      </main>
    </>
  )
}
