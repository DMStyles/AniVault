import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const API = 'http://localhost:8642'

export default function Manga() {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [source, setSource] = useState('auto')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [trending, setTrending] = useState([])

  // Apply manga-mode class to body for amber theme
  useEffect(() => {
    document.body.classList.add('manga-mode')
    return () => document.body.classList.remove('manga-mode')
  }, [])

  // Load trending / popular manga on mount via MangaDex top titles
  useEffect(() => {
    const loadTrending = async () => {
      try {
        const r = await fetch(`${API}/manga/search?q=one+piece&source=mangadex`)
        const data = await r.json()
        // Just use a variety of popular searches to fill the grid
        const r2 = await fetch(`${API}/manga/search?q=naruto&source=mangadex`)
        const data2 = await r2.json()
        const combined = [...(data.results || []).slice(0, 6), ...(data2.results || []).slice(0, 6)]
        setTrending(combined)
      } catch {}
    }
    loadTrending()
  }, [])

  const handleSearch = async (e) => {
    e?.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setSearched(true)
    try {
      const r = await fetch(`${API}/manga/search?q=${encodeURIComponent(query.trim())}&source=${source}`)
      const data = await r.json()
      setResults(data.results || [])
    } catch {
      setResults([])
    }
    setLoading(false)
  }

  const displayResults = searched ? results : trending

  return (
    <div className="manga-page">
      {/* Hero Search Bar */}
      <div className="manga-hero-bar">
        <div className="manga-hero-eyebrow">
          <span className="manga-hero-icon">📚</span>
          <span className="manga-hero-label">Manga Reader</span>
        </div>
        <h1 className="manga-hero-title">Read Manga Online</h1>
        <p className="manga-hero-sub">Search millions of titles across MangaDex and more</p>

        <form className="manga-search-bar" onSubmit={handleSearch}>
          <input
            className="manga-search-input"
            type="text"
            placeholder="Search manga titles, e.g. Naruto, Attack on Titan..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            autoFocus
          />
          <button className="manga-search-btn" type="submit" disabled={loading}>
            {loading ? (
              <span className="spinner" style={{ width: 16, height: 16 }} />
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                Search
              </>
            )}
          </button>
        </form>

        <div className="manga-source-tabs">
          {[
            { id: 'auto', label: '⚡ Auto (Best)' },
            { id: 'mangadex', label: '📖 MangaDex' },
            { id: 'mangakakalot', label: '🔄 MangaKakalot' },
          ].map(s => (
            <button
              key={s.id}
              className={`manga-source-tab${source === s.id ? ' active' : ''}`}
              onClick={() => setSource(s.id)}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Results Grid */}
      <div className="manga-results-section">
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}>
            <span className="spinner" style={{ width: 36, height: 36 }} />
          </div>
        ) : (
          <>
            <div className="manga-results-label">
              {searched
                ? `${displayResults.length} results for "${query}"`
                : '📈 Popular Titles'}
            </div>
            {displayResults.length === 0 && searched ? (
              <div style={{ textAlign: 'center', padding: 60, color: 'var(--text-muted)' }}>
                <div style={{ fontSize: 48, marginBottom: 12 }}>🔍</div>
                <p>No manga found for "{query}".</p>
                <p style={{ fontSize: 12, marginTop: 6 }}>Try a different source or spelling.</p>
              </div>
            ) : (
              <div className="manga-grid">
                {displayResults.map((manga, i) => (
                  <div
                    key={manga.id || i}
                    className="manga-card"
                    onClick={() => navigate(`/manga/${encodeURIComponent(manga.id)}`, { state: { manga } })}
                  >
                    {manga.cover ? (
                      <img
                        className="manga-card-cover"
                        src={manga.cover}
                        alt={manga.title}
                        loading="lazy"
                        onError={e => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex' }}
                      />
                    ) : null}
                    <div className="manga-card-cover-placeholder" style={{ display: manga.cover ? 'none' : 'flex' }}>
                      📚
                    </div>
                    <div className="manga-card-info">
                      <div className="manga-card-title">{manga.title}</div>
                      {manga.status && <div className="manga-card-badge">{manga.status}</div>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
