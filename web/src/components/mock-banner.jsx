import { content } from '../content.js'

// Section 2. Red banner at the very top whenever any loaded file has is_mock: true.
export default function MockBanner({ show }) {
  if (!show) return null
  return (
    <div className="mock-banner" role="status">
      <strong>{content.mockBanner}</strong>
      <span>{content.mockBannerDetail}</span>
    </div>
  )
}
