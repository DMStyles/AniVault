import React, { useContext, useEffect, useRef, useState } from 'react'
import { AppContext } from '../App'

export default function PlayerModal() {
  const { playerModal, setPlayerModal } = useContext(AppContext)
  const videoRef = useRef()
  const iframeRef = useRef()
  const [currentUrl, setCurrentUrl] = useState(playerModal.url)

  useEffect(() => {
    setCurrentUrl(playerModal.url)
  }, [playerModal.url])

  useEffect(() => {
    const handleKey = (e) => { if (e.key === 'Escape') setPlayerModal(null) }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [])

  return (
    <div className="modal-overlay" style={{zIndex:2000}} onClick={(e) => e.target === e.currentTarget && setPlayerModal(null)}>
      <div className="player-panel" style={{ position: 'relative', overflow: 'hidden' }}>
        
        {/* Header Bar */}
        <div className="player-header" style={{display:'flex', alignItems:'center', gap: 12, padding: '10px 16px', background: '#090d16', borderBottom: '1px solid rgba(255,255,255,0.08)'}}>
          <span style={{fontWeight:700, fontSize:14, flex:1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>
            {playerModal.title}
          </span>
          
          {playerModal.alternatives && playerModal.alternatives.length > 1 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ fontSize: 11, color: '#888', fontWeight: 600, textTransform: 'uppercase' }}>Server:</span>
              {playerModal.alternatives.map((alt, i) => {
                const isActive = currentUrl === alt.url
                return (
                  <button
                    key={i}
                    onClick={() => setCurrentUrl(alt.url)}
                    style={{
                      padding: '3px 9px',
                      fontSize: 11,
                      fontWeight: isActive ? 700 : 500,
                      borderRadius: 6,
                      border: '1px solid ' + (isActive ? 'var(--accent, #6366f1)' : 'rgba(255,255,255,0.15)'),
                      background: isActive ? 'var(--accent, #6366f1)' : 'rgba(255,255,255,0.05)',
                      color: isActive ? '#fff' : '#ccc',
                      cursor: 'pointer'
                    }}
                  >
                    {alt.name}
                  </button>
                )
              })}
            </div>
          )}

          <button className="modal-close" onClick={() => setPlayerModal(null)}>✕</button>
        </div>

        {/* Player Media View */}
        {(() => {
          const isDirectVideo = currentUrl.includes('/library/stream') || 
                                currentUrl.includes('.mp4') || 
                                currentUrl.includes('.m3u8') || 
                                currentUrl.includes('.mkv');

          if (isDirectVideo) {
            return (
              <video
                ref={videoRef}
                src={currentUrl}
                controls
                autoPlay
                className="player-video"
                style={{ width: '100%', height: 'calc(100% - 48px)', background: '#000', border: 'none', outline: 'none' }}
              />
            );
          }

          return (
            <iframe
              ref={iframeRef}
              src={currentUrl}
              allowFullScreen
              allow="autoplay; encrypted-media; picture-in-picture"
              className="player-video"
              style={{ width: '100%', height: 'calc(100% - 48px)', background: '#000', border: 'none', outline: 'none' }}
            />
          );
        })()}
      </div>
    </div>
  )
}
