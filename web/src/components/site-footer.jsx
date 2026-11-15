import { content } from '../content.js'

// Section 10. Team, event and challenge name.
export default function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="wrap">
        <p>
          <strong>{content.footerTeam}:</strong> {content.team.join(', ')}
        </p>
        <p>{content.footerEvent}</p>
        {content.challenge && <p>{content.footerChallenge(content.challenge)}</p>}
        <p className="muted">{content.footerData}</p>
      </div>
    </footer>
  )
}
