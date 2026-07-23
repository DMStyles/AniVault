import React, { useState, useEffect, useRef } from 'react'

const EXAMPLE_EXTENSION = `// === KamiWatch Extension Template ===
// Copy this, fill in your scraping logic, and install!

module.exports = {
  manifest: {
    id: "my-source",
    name: "My Anime Source",
    version: "1.0.0",
    type: "anime",           // "anime" | "manga"
    icon: "",                // URL to icon image
    description: "My custom streaming source",
    author: "YourName"
  },

  // Search for anime by title
  async search(query) {
    const res = await fetch(\`https://example.com/search?q=\${encodeURIComponent(query)}\`)
    const html = await res.text()
    // Parse results and return array of:
    // [{ id, title, cover, url, type }]
    return []
  },

  // Get episode list for an anime
  async getEpisodes(url) {
    const res = await fetch(url)
    const html = await res.text()
    // Return array of:
    // [{ number, title, url }]
    return []
  },

  // Resolve a playable stream URL
  async getStreamUrl(episodeUrl) {
    // Return a direct embed or stream URL string
    return episodeUrl
  }
}`

export default function Extensions() {
  const [extensions, setExtensions] = useState([])
  const [loading, setLoading] = useState(true)
  const [installing, setInstalling] = useState(false)
  const [installUrl, setInstallUrl] = useState('')
  const [installCode, setInstallCode] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showCodeEditor, setShowCodeEditor] = useState(false)
  const [showTemplate, setShowTemplate] = useState(false)
  const fileRef = useRef(null)

  useEffect(() => {
    loadExtensions()
  }, [])

  const loadExtensions = async () => {
    setLoading(true)
    try {
      const list = await window.electronAPI?.extensions?.list() || []
      setExtensions(list)
    } catch (e) {
      setExtensions([])
    } finally {
      setLoading(false)
    }
  }

  const handleInstallUrl = async () => {
    if (!installUrl.trim()) { setError('Please enter a URL'); return }
    setInstalling(true)
    setError('')
    setSuccess('')
    try {
      const result = await window.electronAPI?.extensions?.install({ url: installUrl.trim() })
      if (result?.success) {
        setSuccess(`✅ Extension "${result.manifest.name}" installed successfully!`)
        setInstallUrl('')
        await loadExtensions()
      } else {
        setError(result?.error || 'Failed to install extension')
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setInstalling(false)
    }
  }

  const handleInstallCode = async () => {
    if (!installCode.trim()) { setError('Please paste extension code'); return }
    setInstalling(true)
    setError('')
    setSuccess('')
    try {
      const result = await window.electronAPI?.extensions?.install({ code: installCode.trim() })
      if (result?.success) {
        setSuccess(`✅ Extension "${result.manifest.name}" installed successfully!`)
        setInstallCode('')
        setShowCodeEditor(false)
        await loadExtensions()
      } else {
        setError(result?.error || 'Failed to install extension')
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setInstalling(false)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const code = await file.text()
    setInstallCode(code)
    setShowCodeEditor(true)
    e.target.value = ''
  }

  const handleRemove = async (id, name) => {
    if (!window.confirm(`Remove extension "${name}"?`)) return
    try {
      await window.electronAPI?.extensions?.remove(id)
      setSuccess(`Extension "${name}" removed.`)
      await loadExtensions()
    } catch (e) {
      setError(e.message)
    }
  }

  const cardStyle = {
    background: 'rgba(13,13,26,0.75)',
    backdropFilter: 'blur(18px)',
    border: '1px solid rgba(255,255,255,0.07)',
    borderRadius: 16,
    padding: 24,
    marginBottom: 20,
  }

  const sectionTitle = {
    fontSize: 15,
    fontWeight: 700,
    color: 'var(--text-primary)',
    marginBottom: 16,
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  }

  return (
    <div style={{ maxWidth: 820, margin: '0 auto', padding: '28px 24px 60px' }}>
      {/* Page Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 26, fontWeight: 900, letterSpacing: '-0.03em', marginBottom: 8 }}>
          🧩 Extensions
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.7 }}>
          Extend KamiWatch with community-made scrapers. Install extensions to add new anime and manga sources without updating the app.
        </p>
      </div>

      {/* Alerts */}
      {error && (
        <div style={{ background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 10, padding: '12px 16px', marginBottom: 16, fontSize: 13, color: '#f87171' }}>
          ❌ {error}
          <button onClick={() => setError('')} style={{ float: 'right', background: 'none', border: 'none', color: '#f87171', cursor: 'pointer', fontSize: 16, lineHeight: 1 }}>×</button>
        </div>
      )}
      {success && (
        <div style={{ background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 10, padding: '12px 16px', marginBottom: 16, fontSize: 13, color: '#34d399' }}>
          {success}
          <button onClick={() => setSuccess('')} style={{ float: 'right', background: 'none', border: 'none', color: '#34d399', cursor: 'pointer', fontSize: 16, lineHeight: 1 }}>×</button>
        </div>
      )}

      {/* ── Install by URL ─────────────────────────────────── */}
      <div style={cardStyle}>
        <div style={sectionTitle}>
          <span style={{ width: 3, height: 16, background: 'linear-gradient(135deg, #7c3aed, #06b6d4)', borderRadius: 2, display: 'block' }} />
          Install from URL
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 14 }}>
          Paste a direct link to a <code style={{ background: 'rgba(255,255,255,0.07)', padding: '2px 6px', borderRadius: 4, fontSize: 12 }}>.js</code> extension file hosted on GitHub, Pastebin, or any raw URL.
        </p>
        <div style={{ display: 'flex', gap: 10 }}>
          <input
            value={installUrl}
            onChange={e => setInstallUrl(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleInstallUrl()}
            placeholder="https://raw.githubusercontent.com/user/repo/main/extension.js"
            style={{
              flex: 1, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 8, padding: '10px 14px', color: 'var(--text-primary)', fontSize: 13,
              outline: 'none', transition: 'border-color 0.2s',
            }}
            onFocus={e => e.target.style.borderColor = 'rgba(124,58,237,0.6)'}
            onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
          />
          <button
            className="btn btn-primary"
            onClick={handleInstallUrl}
            disabled={installing}
            style={{ whiteSpace: 'nowrap', minWidth: 100 }}
          >
            {installing ? <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> : '⬇ Install'}
          </button>
        </div>
      </div>

      {/* ── Install by File / Code ─────────────────────────── */}
      <div style={cardStyle}>
        <div style={sectionTitle}>
          <span style={{ width: 3, height: 16, background: 'linear-gradient(135deg, #7c3aed, #06b6d4)', borderRadius: 2, display: 'block' }} />
          Install from File or Code
        </div>
        <div style={{ display: 'flex', gap: 10, marginBottom: showCodeEditor ? 14 : 0, flexWrap: 'wrap' }}>
          <button
            className="btn btn-secondary"
            onClick={() => fileRef.current?.click()}
          >
            📁 Upload .js File
          </button>
          <input ref={fileRef} type="file" accept=".js" onChange={handleFileUpload} style={{ display: 'none' }} />
          <button
            className="btn btn-secondary"
            onClick={() => setShowCodeEditor(!showCodeEditor)}
          >
            {showCodeEditor ? '▲ Hide Code Editor' : '✏️ Paste Extension Code'}
          </button>
          <button
            className="btn btn-ghost"
            onClick={() => { setShowTemplate(!showTemplate) }}
            style={{ fontSize: 12 }}
          >
            {showTemplate ? '▲ Hide Template' : '📋 Show Extension Template'}
          </button>
        </div>

        {showTemplate && (
          <pre style={{
            background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: 10, padding: 16, fontSize: 11, color: 'var(--text-secondary)',
            overflowX: 'auto', marginBottom: 14, lineHeight: 1.6, maxHeight: 300, overflowY: 'auto',
          }}>
            {EXAMPLE_EXTENSION}
          </pre>
        )}

        {showCodeEditor && (
          <>
            <textarea
              value={installCode}
              onChange={e => setInstallCode(e.target.value)}
              placeholder={`Paste your extension JavaScript code here...\n\nExample:\nmodule.exports = {\n  manifest: { name: "My Source", version: "1.0.0", type: "anime" },\n  async search(query) { return [] },\n  async getEpisodes(url) { return [] },\n  async getStreamUrl(episodeUrl) { return episodeUrl }\n}`}
              style={{
                width: '100%', height: 200, background: 'rgba(0,0,0,0.4)',
                border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10,
                padding: 14, color: 'var(--text-primary)', fontSize: 12,
                fontFamily: '"Fira Code", "Cascadia Code", monospace',
                resize: 'vertical', outline: 'none', lineHeight: 1.6,
                marginBottom: 12,
              }}
            />
            <button
              className="btn btn-primary"
              onClick={handleInstallCode}
              disabled={installing}
            >
              {installing ? <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> : '⬇ Install Extension'}
            </button>
          </>
        )}
      </div>

      {/* ── Installed Extensions ───────────────────────────── */}
      <div style={cardStyle}>
        <div style={sectionTitle}>
          <span style={{ width: 3, height: 16, background: 'linear-gradient(135deg, #7c3aed, #06b6d4)', borderRadius: 2, display: 'block' }} />
          Installed Extensions
          <span style={{ marginLeft: 'auto', fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', background: 'rgba(255,255,255,0.06)', padding: '3px 10px', borderRadius: 99 }}>
            {extensions.length} installed
          </span>
        </div>

        {loading ? (
          <div style={{ display: 'flex', gap: 14, padding: '20px 0' }}>
            {[1,2].map(i => <div key={i} className="skeleton" style={{ flex: 1, height: 80, borderRadius: 10 }} />)}
          </div>
        ) : extensions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '36px 0', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>🧩</div>
            <p style={{ fontSize: 14, fontWeight: 600 }}>No extensions installed yet</p>
            <p style={{ fontSize: 12, marginTop: 6 }}>Install an extension above to add new streaming sources</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {extensions.map(ext => (
              <div
                key={ext.id}
                style={{
                  display: 'flex', alignItems: 'center', gap: 14,
                  background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)',
                  borderRadius: 12, padding: '12px 16px',
                  transition: 'border-color 0.2s',
                }}
                onMouseEnter={e => e.currentTarget.style.borderColor = 'rgba(124,58,237,0.3)'}
                onMouseLeave={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)'}
              >
                {/* Icon */}
                <div style={{
                  width: 44, height: 44, borderRadius: 10, overflow: 'hidden',
                  background: 'linear-gradient(135deg, #7c3aed, #06b6d4)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 22, flexShrink: 0,
                }}>
                  {ext.manifest.icon ? (
                    <img src={ext.manifest.icon} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} onError={e => e.target.style.display = 'none'} />
                  ) : '🧩'}
                </div>

                {/* Info */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 2 }}>
                    {ext.manifest.name}
                    <span style={{ marginLeft: 8, fontSize: 11, color: 'var(--text-muted)', fontWeight: 500 }}>
                      v{ext.manifest.version}
                    </span>
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {ext.manifest.description || 'No description'}
                  </div>
                </div>

                {/* Badges */}
                <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
                  <span style={{
                    padding: '3px 9px', borderRadius: 99, fontSize: 11, fontWeight: 600,
                    background: ext.manifest.type === 'anime' ? 'rgba(124,58,237,0.15)' : 'rgba(217,119,6,0.15)',
                    color: ext.manifest.type === 'anime' ? 'var(--accent-light)' : '#fbbf24',
                    border: `1px solid ${ext.manifest.type === 'anime' ? 'rgba(124,58,237,0.3)' : 'rgba(217,119,6,0.3)'}`,
                    textTransform: 'capitalize',
                  }}>
                    {ext.manifest.type}
                  </span>
                  {ext.manifest.author && (
                    <span style={{ padding: '3px 9px', borderRadius: 99, fontSize: 11, fontWeight: 500, background: 'rgba(255,255,255,0.05)', color: 'var(--text-muted)', border: '1px solid rgba(255,255,255,0.06)' }}>
                      by {ext.manifest.author}
                    </span>
                  )}
                </div>

                {/* Remove */}
                <button
                  onClick={() => handleRemove(ext.id, ext.manifest.name)}
                  style={{
                    background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)',
                    color: '#f87171', borderRadius: 8, padding: '6px 12px',
                    fontSize: 12, fontWeight: 600, cursor: 'pointer',
                    transition: 'all 0.2s', flexShrink: 0,
                  }}
                  onMouseEnter={e => { e.currentTarget.style.background = 'rgba(239,68,68,0.2)'; e.currentTarget.style.borderColor = 'rgba(239,68,68,0.4)' }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'rgba(239,68,68,0.1)'; e.currentTarget.style.borderColor = 'rgba(239,68,68,0.2)' }}
                >
                  🗑 Remove
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Extension Format Docs ──────────────────────────── */}
      <div style={{ ...cardStyle, background: 'rgba(124,58,237,0.06)', borderColor: 'rgba(124,58,237,0.2)' }}>
        <div style={{ ...sectionTitle, color: 'var(--accent-light)' }}>
          📖 Extension API Reference
        </div>
        <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.8 }}>
          <p style={{ marginBottom: 12 }}>Extensions are CommonJS <code style={{ background: 'rgba(255,255,255,0.07)', padding: '1px 5px', borderRadius: 4, fontSize: 12 }}>.js</code> files that export these members:</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {[
              { name: 'manifest', type: 'object', desc: 'id, name, version, type, icon, description, author' },
              { name: 'search(query)', type: 'async fn', desc: 'Returns [{ id, title, cover, url }]' },
              { name: 'getEpisodes(url)', type: 'async fn', desc: 'Returns [{ number, title, url }]' },
              { name: 'getStreamUrl(url)', type: 'async fn', desc: 'Returns a playable URL string' },
            ].map(({ name, type, desc }) => (
              <div key={name} style={{ display: 'flex', gap: 12, padding: '8px 12px', background: 'rgba(0,0,0,0.2)', borderRadius: 8, alignItems: 'flex-start' }}>
                <code style={{ color: 'var(--accent-light)', fontWeight: 700, fontSize: 12, minWidth: 160, fontFamily: 'monospace' }}>{name}</code>
                <span style={{ color: 'var(--text-muted)', fontSize: 11, fontWeight: 600, minWidth: 70, marginTop: 1 }}>{type}</span>
                <span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{desc}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
