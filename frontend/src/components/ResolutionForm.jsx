import React, { useState } from 'react'
import { Save, Loader2 } from 'lucide-react'

export default function ResolutionForm({ onSubmit, loading }) {
  const [form, setForm] = useState({
    root_cause: '',
    fix: '',
    outcome: '',
    resolution_time_minutes: '',
  })

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = (e) => {
    e.preventDefault()
    const payload = {
      root_cause: form.root_cause,
      fix: form.fix,
      outcome: form.outcome,
    }
    if (form.resolution_time_minutes) {
      payload.resolution_time_minutes = parseInt(form.resolution_time_minutes, 10)
    }
    onSubmit(payload)
  }

  const inputClass = "w-full bg-slate-800/80 border border-slate-600/60 rounded-lg px-3 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-colors"
  const labelClass = "block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wide"

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className={labelClass}>Root Cause *</label>
        <textarea
          className={`${inputClass} resize-none`}
          rows={3}
          placeholder="What was the actual root cause of this incident?"
          value={form.root_cause}
          onChange={set('root_cause')}
          required
          minLength={5}
        />
      </div>

      <div>
        <label className={labelClass}>Fix Applied *</label>
        <textarea
          className={`${inputClass} resize-none`}
          rows={3}
          placeholder="What steps were taken to fix the incident?"
          value={form.fix}
          onChange={set('fix')}
          required
          minLength={5}
        />
      </div>

      <div>
        <label className={labelClass}>Outcome *</label>
        <textarea
          className={`${inputClass} resize-none`}
          rows={2}
          placeholder="What was the result? Did the service recover? Any follow-up needed?"
          value={form.outcome}
          onChange={set('outcome')}
          required
          minLength={5}
        />
      </div>

      <div>
        <label className={labelClass}>Resolution Time (minutes)</label>
        <input
          type="number"
          className={inputClass}
          placeholder="e.g. 35"
          value={form.resolution_time_minutes}
          onChange={set('resolution_time_minutes')}
          min={1}
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 bg-green-600 hover:bg-green-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-xl transition-colors"
      >
        {loading ? (
          <><Loader2 size={16} className="animate-spin" /> Storing in Memory...</>
        ) : (
          <><Save size={16} /> Save & Store in Hindsight Memory</>
        )}
      </button>
    </form>
  )
}
