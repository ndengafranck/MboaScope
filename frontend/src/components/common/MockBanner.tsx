export function MockBanner({ show }: { show: boolean }) {
  if (!show) return null
  return (
    <div className="mock-banner" role="note">
      <strong>Demo data.</strong> These numbers come from synthetic rainfall, not NASA. Do not quote them.
    </div>
  )
}
