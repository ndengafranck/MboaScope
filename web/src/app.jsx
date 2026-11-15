import { Suspense, lazy } from 'react'
import AnswerCard from './components/answer-card.jsx'
import Explanation from './components/explanation.jsx'
import Limitations from './components/limitations.jsx'
import MethodAndData from './components/method-and-data.jsx'
import MockBanner from './components/mock-banner.jsx'
import RobustnessTable from './components/robustness-table.jsx'
import SiteFooter from './components/site-footer.jsx'
import SiteHeader from './components/site-header.jsx'
import TrendMap from './components/trend-map.jsx'
import { content } from './content.js'
import { useData } from './lib/load-data.js'

// recharts is the heaviest dependency: load it as its own chunk so the answer shows first.
const AnnualChart = lazy(() => import('./components/annual-chart.jsx'))

function SectionFallback({ title }) {
  return (
    <section className="section">
      <h2>{title}</h2>
      <p className="state" aria-busy="true">
        {content.loading}
      </p>
    </section>
  )
}

// The one page, ten sections top to bottom. Shows numbers from the JSON files
// only; computes no statistics.
export default function App() {
  const { files, isMock } = useData()
  const { annual, analysis, spatial, explanation, provenance } = files

  return (
    <>
      <MockBanner show={isMock} />
      <SiteHeader provenance={provenance} />
      <main className="wrap">
        <AnswerCard analysis={analysis} annual={annual} />
        <Suspense fallback={<SectionFallback title={content.chartHeading} />}>
          <AnnualChart annual={annual} analysis={analysis} />
        </Suspense>
        <TrendMap spatial={spatial} annual={annual} analysis={analysis} />
        <RobustnessTable analysis={analysis} annual={annual} />
        <Explanation explanation={explanation} />
        <Limitations explanation={explanation} />
        <MethodAndData provenance={provenance} />
      </main>
      <SiteFooter />
    </>
  )
}
