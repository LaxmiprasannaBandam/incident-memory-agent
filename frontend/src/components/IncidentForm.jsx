import React, { useState } from 'react'
import { Send, Loader2 } from 'lucide-react'

const SEVERITY_OPTIONS = ['critical', 'high', 'medium', 'low']
const ENV_OPTIONS = ['production', 'staging', 'dev']

export default function IncidentForm({ onSubmit, loading }) {
  const [form, setForm] = useState({
    title: '',
    service: '',
    environment: 'production',
    severity: 'high',
    description: '',
    logs: '',
    recent_changes: '',
  })

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(form)
  }

  const inputClass = "w-full bg-slate-800/80 border border-slate-600/60 rounded-lg px-3 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-colors"
  const labelClass = "block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wide"

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className={labelClass}>Incident Title *</label>
        <input
          className={inputClass}
          placeholder="e.g. Payment API returns 503 errors after deployment"
          value={form.title}
          onChange={set('title')}
          required
          minLength={3}
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Service *</label>
          <input
            className={inputClass}
            placeholder="e.g. payment-api"
            value={form.service}
            onChange={set('service')}
            required
          />
        </div>
        <div>
          <label className={labelClass}>Environment</label>
          <select className={inputClass} value={form.environment} onChange={set('environment')}>
            {ENV_OPTIONS.map(e => <option key={e} value={e}>{e}</option>)}
          </select>
        </div>
      </div>

      <div>
        <label className={labelClass}>Severity</label>
        <div className="grid grid-cols-4 gap-2">
          {SEVERITY_OPTIONS.map(s => (
            <button
              key={s}
              type="button"
              onClick={() => setForm({ ...form, severity: s })}
              className={`py-2 rounded-lg text-xs font-semibold border transition-colors ${
                form.severity === s
                  ? s === 'critical' ? 'bg-red-500/30 border-red-500/60 text-red-300'
                  : s === 'high' ? 'bg-orange-500/30 border-orange-500/60 text-orange-300'
                  : s === 'medium' ? 'bg-yellow-500/30 border-yellow-500/60 text-yellow-300'
                  : 'bg-green-500/30 border-green-500/60 text-green-300'
                  : 'bg-slate-800 border-slate-600/60 text-slate-400 hover:border-slate-500'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className={labelClass}>Description *</label>
        <textarea
          className={`${inputClass} resize-none`}
          rows={3}
          placeholder="Describe what is happening. Include impact, affected users, timeline..."
          value={form.description}
          onChange={set('description')}
          required
          minLength={10}
        />
      </div>

      <div>
        <label className={labelClass}>Error Logs / Output</label>
        <textarea
          className={`${inputClass} font-mono text-xs resize-none`}
          rows={4}
          placeholder="Paste relevant error messages, stack traces, or log output..."
          value={form.logs}
          onChange={set('logs')}
        />
      </div>

      <div>
        <label className={labelClass}>Recent Changes / Deployments</label>
        <textarea
          className={`${inputClass} resize-none`}
          rows={2}
          placeholder="Any recent deployments, config changes, or infrastructure updates?"
          value={form.recent_changes}
          onChange={set('recent_changes')}
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-xl transition-colors"
      >
        {loading ? (
          <><Loader2 size={16} className="animate-spin" /> Analyzing...</>
        ) : (
          <><Send size={16} /> Analyze Incident</>
        )}
      </button>
    </form>
  )
}
