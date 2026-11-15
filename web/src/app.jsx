import { Suspense, lazy } from 'react'
import AnswerCard from './components/answer-card.jsx'
import Explanation from './components/explanation.jsx'
import Limitations from './components/limitations.jsx'
import MethodAndData from './components/method-and-data.jsx'
import MockBanner from './components/mock-banner.jsx'
import RobustnessTable from './components/robustness-table.jsx'
import SiteFooter from './components/site-footer.jsx'
import SiteHeader from './components/site-header.jsx'
import TopBar from './components/top-bar.jsx'
import TrendMap from './components/trend-map.jsx'
import { content } from './content.js'
import { useData } from './lib/load-data.js'

// recharts is the heaviest dependency: load it as its own chunk so the answer shows first.
const AnnualChart = lazy(() => import('./components/annual-chart.jsx'))

function SectionFallback({ id, title }) {
  return (
    <section className="card" id={id}>
      <header className="card-head">
        <div className="card-titles">
          <h2>{title}</h2>
        </div>
      </header>
      <div className="card-body">
        <div className="skeleton" aria-busy="true">
          <span className="sr-only">{content.loading}</span>
          <span className="sk sk-1" />
          <span className="sk sk-2" />
          <span className="sk sk-3" />
        </div>
      </div>
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
      <a className="skip" href="#answer">
        {content.skip}
      </a>
      <MockBanner show={isMock} />
      <TopBar isMock={isMock} />
      <SiteHeader provenance={provenance} />
      <main className="container layout">
        <div className="span-12 lift">
          <AnswerCard analysis={analysis} annual={annual} />
        </div>
        <div className="span-12">
          <Suspense fallback={<SectionFallback id="chart" title={content.chartHeading} />}>
            <AnnualChart annual={annual} analysis={analysis} />
          </Suspense>
        </div>
        <div className="span-12">
          <TrendMap spatial={spatial} annual={annual} analysis={analysis} />
        </div>
        <div className="span-12">
          <RobustnessTable analysis={analysis} annual={annual} />
        </div>
        <div className="span-7">
          <Explanation explanation={explanation} />
        </div>
        <div className="span-5">
          <Limitations explanation={explanation} />
        </div>
        <div className="span-12">
          <MethodAndData provenance={provenance} />
        </div>
      </main>
      <SiteFooter />
    </>
  )
}
