import { useEffect, useState } from 'react'
import { content } from '../content.js'
import { REPO_URL } from '../lib/science.js'
import { IconGithub } from './icons.jsx'

// Sticky app bar: brand, section navigation with the current section
// highlighted, and a link to the source code.
export default function TopBar({ isMock }) {
  const [active, setActive] = useState(content.nav[0].id)

  useEffect(() => {
    const els = content.nav.map((n) => document.getElementById(n.id)).filter(Boolean)
    if (!('IntersectionObserver' in window) || els.length === 0) return undefined
    const io = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        if (visible[0]) setActive(visible[0].target.id)
      },
      { rootMargin: '-96px 0px -55% 0px' },
    )
    els.forEach((el) => io.observe(el))
    return () => io.disconnect()
  }, [])

  return (
    <div className="topbar">
      <div className="flag-strip" aria-hidden="true">
        <span />
        <span>
          <svg viewBox="0 0 24 24" width="9" height="9">
            <path d="M12 2l2.9 6.9 7.1.6-5.4 4.7 1.7 7-6.3-3.9-6.3 3.9 1.7-7L2 9.5l7.1-.6z" fill="#fcd116" />
          </svg>
        </span>
        <span />
      </div>
      <div className="container topbar-inner">
        <a className="logo" href="#top" aria-label={content.title}>
          <span className="logo-mark" aria-hidden="true">
            <svg viewBox="0 0 32 32" width="28" height="28">
              <rect x="1" y="1" width="30" height="30" rx="10" fill="var(--brand)" />
              <circle cx="23" cy="9" r="4" fill="var(--sun)" />
              <path d="M14 7c3.6 4.3 6.2 7.7 6.2 10.7a6.2 6.2 0 0 1-12.4 0C7.8 14.7 10.4 11.3 14 7z" fill="#fffaf0" />
              <path d="M10.8 20l2.3-2.3 1.8 1.8 2.7-2.7" stroke="var(--brand)" strokeWidth="1.7" fill="none" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </span>
          <span className="logo-text">{content.title}</span>
          {isMock && <span className="badge badge-alert">{content.mockBadge}</span>}
        </a>
        <nav className="nav" aria-label={content.navLabel}>
          {content.nav.map((n) => (
            <a key={n.id} href={`#${n.id}`} className={active === n.id ? 'is-active' : ''} aria-current={active === n.id ? 'true' : undefined}>
              {n.label}
            </a>
          ))}
        </nav>
        <a className="icon-btn" href={REPO_URL} aria-label={content.methodRepo}>
          <IconGithub />
        </a>
      </div>
    </div>
  )
}
