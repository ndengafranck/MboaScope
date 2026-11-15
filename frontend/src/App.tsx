import { lazy, Suspense } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Layout } from './components/common/Layout'
import { Loading } from './components/common/Status'
import { InvestigationProvider } from './hooks/useInvestigation'
import Dashboard from './pages/Dashboard'

// Leaflet and the larger pages load on demand so the dashboard answer appears first.
const Explorer = lazy(() => import('./pages/Explorer'))
const Analysis = lazy(() => import('./pages/Analysis'))
const Assistant = lazy(() => import('./pages/Assistant'))

export default function App() {
  return (
    <BrowserRouter>
      <InvestigationProvider>
        <Suspense fallback={<Loading />}>
          <Routes>
            <Route element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="explorer" element={<Explorer />} />
              <Route path="analysis" element={<Analysis />} />
              <Route path="assistant" element={<Assistant />} />
              <Route path="*" element={<Dashboard />} />
            </Route>
          </Routes>
        </Suspense>
      </InvestigationProvider>
    </BrowserRouter>
  )
}
