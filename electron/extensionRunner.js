/**
 * KamiWatch Extension Runner
 * Sandboxes and executes community-written extension scripts using Node's vm module.
 * Each extension is a CommonJS module that exports: manifest, search, getEpisodes, getStreamUrl
 */

const vm = require('vm')
const http = require('http')
const https = require('https')

class ExtensionRunner {
  constructor() {
    /** @type {Map<string, { code: string, module: object }>} */
    this.extensions = new Map()
  }

  /**
   * Create a safe sandbox with limited globals for extension code to run in.
   * Extensions get access to fetch, console, JSON, URL, URLSearchParams.
   */
  _createSandbox() {
    // Minimal fetch polyfill for the sandbox
    const sandboxFetch = (url, options = {}) => {
      return new Promise((resolve, reject) => {
        try {
          const urlObj = new URL(url)
          const isHttps = urlObj.protocol === 'https:'
          const lib = isHttps ? https : http
          const reqOptions = {
            hostname: urlObj.hostname,
            port: urlObj.port || (isHttps ? 443 : 80),
            path: urlObj.pathname + urlObj.search,
            method: options.method || 'GET',
            headers: {
              'User-Agent': 'KamiWatch/3.0 Extension Runner',
              ...(options.headers || {}),
            },
          }
          const req = lib.request(reqOptions, (res) => {
            let data = ''
            res.on('data', chunk => { data += chunk })
            res.on('end', () => {
              resolve({
                ok: res.statusCode >= 200 && res.statusCode < 300,
                status: res.statusCode,
                text: () => Promise.resolve(data),
                json: () => Promise.resolve(JSON.parse(data)),
              })
            })
          })
          req.on('error', reject)
          if (options.body) req.write(options.body)
          req.end()
        } catch (e) {
          reject(e)
        }
      })
    }

    return {
      fetch: sandboxFetch,
      console: {
        log: (...args) => console.log('[Extension]', ...args),
        error: (...args) => console.error('[Extension]', ...args),
        warn: (...args) => console.warn('[Extension]', ...args),
      },
      module: { exports: {} },
      exports: {},
      setTimeout,
      clearTimeout,
      setInterval,
      clearInterval,
      JSON,
      URL,
      URLSearchParams,
      RegExp,
      Array,
      Object,
      String,
      Number,
      Math,
      Date,
      Promise,
      Error,
      parseInt,
      parseFloat,
      decodeURIComponent,
      encodeURIComponent,
      atob: (s) => Buffer.from(s, 'base64').toString('binary'),
      btoa: (s) => Buffer.from(s, 'binary').toString('base64'),
    }
  }

  /**
   * Load and validate an extension from source code.
   * @param {string} id - Unique extension identifier
   * @param {string} code - Extension JavaScript source code
   * @returns {{ success: boolean, manifest?: object, error?: string }}
   */
  async loadExtension(id, code) {
    try {
      const sandbox = this._createSandbox()
      const script = new vm.Script(`
        (function(module, exports) {
          ${code}
        })(module, exports)
      `)
      const context = vm.createContext(sandbox)
      script.runInContext(context, { timeout: 10000 })

      const ext = sandbox.module.exports
      if (!ext.manifest) throw new Error('Extension is missing a "manifest" export')
      if (!ext.manifest.name) throw new Error('Extension manifest is missing "name"')
      if (!ext.manifest.version) throw new Error('Extension manifest is missing "version"')
      if (!ext.manifest.type) throw new Error('Extension manifest is missing "type" (anime|manga)')

      this.extensions.set(id, { code, module: ext })
      return { success: true, manifest: ext.manifest }
    } catch (e) {
      return { success: false, error: e.message }
    }
  }

  /**
   * Call a function exported by an extension.
   * @param {string} id - Extension ID
   * @param {string} fnName - Function name to call (search, getEpisodes, getStreamUrl)
   * @param {Array} args - Arguments to pass
   * @returns {{ result?: any, error?: string }}
   */
  async callFunction(id, fnName, args = []) {
    const ext = this.extensions.get(id)
    if (!ext) return { error: `Extension "${id}" is not loaded` }

    const fn = ext.module[fnName]
    if (typeof fn !== 'function') return { error: `Function "${fnName}" not found in extension "${id}"` }

    try {
      const result = await Promise.race([
        fn(...args),
        new Promise((_, reject) => setTimeout(() => reject(new Error('Extension call timed out after 30s')), 30000)),
      ])
      return { result }
    } catch (e) {
      return { error: e.message }
    }
  }

  /**
   * Get list of all loaded extensions with their manifests.
   * @returns {Array<{ id: string, manifest: object }>}
   */
  getLoadedExtensions() {
    const list = []
    for (const [id, ext] of this.extensions.entries()) {
      if (id !== '__test__') {
        list.push({ id, manifest: ext.module.manifest })
      }
    }
    return list
  }

  /**
   * Remove an extension by ID.
   * @param {string} id
   */
  unloadExtension(id) {
    this.extensions.delete(id)
  }
}

module.exports = new ExtensionRunner()
