import { content } from '../content.js'
import { REPO_URL } from '../lib/science.js'
import { IconGithub } from './icons.jsx'

// Section 10. Team, event and challenge name.
export default function SiteFooter() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <div>
          <p className="footer-brand">{content.title}</p>
          <p className="footer-muted">{content.footerEvent}</p>
          {content.challenge && <p className="footer-muted">{content.footerChallenge(content.challenge)}</p>}
        </div>
        <div>
          <p className="footer-k">{content.footerTeam}</p>
          <ul className="team">
            {content.team.map((name) => (
              <li key={name}>{name}</li>
            ))}
          </ul>
        </div>
        <div>
          <p className="footer-k">{content.footerSource}</p>
          <p className="footer-muted">{content.footerData}</p>
          <a className="footer-link" href={REPO_URL}>
            <IconGithub size={16} /> {content.methodRepo}
          </a>
        </div>
      </div>
    </footer>
  )
}
