import React from 'react'

/**
 * SkeletonCard - shimmer placeholder for loading states
 * variant: 'anime' | 'hero' | 'episode' | 'character' | 'schedule'
 */
export default function SkeletonCard({ variant = 'anime', count = 1 }) {
  const items = Array.from({ length: count }, (_, i) => i)

  if (variant === 'hero') {
    return (
      <div style={{ padding: '0 24px 16px' }}>
        <div className="skeleton" style={{ height: '56vh', minHeight: 360, borderRadius: 18, marginBottom: 0 }} />
      </div>
    )
  }

  if (variant === 'character') {
    return (
      <>
        {items.map(i => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, flexShrink: 0 }}>
            <div className="skeleton" style={{ width: 72, height: 72, borderRadius: '50%' }} />
            <div className="skeleton" style={{ width: 60, height: 10, borderRadius: 6 }} />
          </div>
        ))}
      </>
    )
  }

  if (variant === 'episode') {
    return (
      <>
        {items.map(i => (
          <div key={i} style={{ display: 'flex', gap: 12, padding: '10px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
            <div className="skeleton" style={{ width: 120, height: 68, borderRadius: 8, flexShrink: 0 }} />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8, paddingTop: 4 }}>
              <div className="skeleton" style={{ width: '40%', height: 10, borderRadius: 6 }} />
              <div className="skeleton" style={{ width: '70%', height: 10, borderRadius: 6 }} />
            </div>
          </div>
        ))}
      </>
    )
  }

  if (variant === 'schedule') {
    return (
      <>
        {items.map(i => (
          <div key={i} style={{ display: 'flex', gap: 14, padding: '12px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
            <div className="skeleton" style={{ width: 54, height: 76, borderRadius: 8, flexShrink: 0 }} />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8, paddingTop: 6 }}>
              <div className="skeleton" style={{ width: '60%', height: 10, borderRadius: 6 }} />
              <div className="skeleton" style={{ width: '35%', height: 10, borderRadius: 6 }} />
            </div>
          </div>
        ))}
      </>
    )
  }

  // Default: anime card
  return (
    <>
      {items.map(i => (
        <div key={i} style={{ flexShrink: 0, width: 150 }}>
          <div className="skeleton" style={{ width: 150, height: 215, borderRadius: 12, marginBottom: 8 }} />
          <div className="skeleton" style={{ width: '80%', height: 10, borderRadius: 6, marginBottom: 6 }} />
          <div className="skeleton" style={{ width: '50%', height: 9, borderRadius: 6 }} />
        </div>
      ))}
    </>
  )
}
