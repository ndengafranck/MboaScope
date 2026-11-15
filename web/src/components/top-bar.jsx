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
      <div className="container topbar-inner">
        <a className="logo" href="#top" aria-label={content.title}>
          <span className="logo-mark" aria-hidden="true">
            <svg viewBox="0 0 32 32" width="28" height="28">
              <circle cx="16" cy="16" r="15" fill="var(--brand)" />
              <path d="M16 6c3.8 4.6 6.6 8.2 6.6 11.4a6.6 6.6 0 0 1-13.2 0C9.4 14.2 12.2 10.6 16 6z" fill="#fff" />
              <path d="M12.4 19.6l2.6-2.6 2 2 3-3" stroke="var(--brand)" strokeWidth="1.8" fill="none" strokeLinecap="round" strokeLinejoin="round" />
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
