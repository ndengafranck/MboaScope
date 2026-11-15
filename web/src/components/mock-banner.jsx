import { content } from '../content.js'
import { IconAlert } from './icons.jsx'

// Section 2. Red banner at the very top whenever any loaded file has is_mock: true.
export default function MockBanner({ show }) {
  if (!show) return null
  return (
    <div className="mock-banner" role="status">
      <div className="container mock-inner">
        <IconAlert size={16} />
        <strong>{content.mockBanner}</strong>
        <span className="mock-detail">{content.mockBannerDetail}</span>
      </div>
    </div>
  )
}
