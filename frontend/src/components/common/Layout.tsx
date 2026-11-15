import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useInvestigation } from '../../hooks/useInvestigation'
import { InvestigationControls } from '../dashboard/InvestigationControls'
import { MockBanner } from './MockBanner'

const NAV = [
  { to: '/', label: 'Dashboard' },
  { to: '/explorer', label: 'Explorer' },
  { to: '/analysis', label: 'Analysis' },
  { to: '/assistant', label: 'Assistant' },
]

export function Layout() {
  const { region } = useInvestigation()
  const { search } = useLocation() // keep ?region=&from=&to= when switching pages
  return (
    <>
      <a className="skip" href="#main">
        Skip to content
      </a>
      <MockBanner show={region?.access_method === 'mock'} />
      <header className="topbar">
        <div className="container topbar-inner">
          <NavLink to={{ pathname: '/', search }} className="brand">
            <span className="brand-mark" aria-hidden="true" />
            MboaScope
          </NavLink>
          <nav aria-label="Main">
            {NAV.map((item) => (
              <NavLink key={item.to} to={{ pathname: item.to, search }} end={item.to === '/'} className="nav-link">
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <div className="controls-bar">
        <div className="container">
          <InvestigationControls />
        </div>
      </div>
      <main id="main" className="container page">
        <Outlet />
      </main>
      <footer className="footer">
        <div className="container">
          Rainfall: NASA GPM IMERG Final, monthly, V07 (GPM_3IMERGM),{' '}
          <a href="https://doi.org/10.5067/GPM/IMERG/3B-MONTH/07">doi:10.5067/GPM/IMERG/3B-MONTH/07</a>. Satellite
          estimates averaged over an area, not station measurements.
        </div>
      </footer>
    </>
  )
}
