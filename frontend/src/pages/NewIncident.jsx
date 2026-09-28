import React, { useState } from 'react'
import toast from 'react-hot-toast'
import { AlertTriangle } from 'lucide-react'
import IncidentForm from '../components/IncidentForm'
import AnalysisPanel from '../components/AnalysisPanel'
import { analyzeIncident } from '../api'

export default function NewIncident() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleSubmit = async (formData) => {
    setLoading(true)
    setResult(null)
    try {
      const response = await analyzeIncident(formData)
      setResult(response.data)
      if (response.data.memory_recall?.found) {
        toast.success('Relevant historical incidents found in memory!', { icon: '🧠' })
      } else {
        toast.success('Incident analyzed successfully')
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Analysis failed'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1">
          <AlertTriangle size={20} className="text-orange-400" />
          <h2 className="text-xl font-bold text-white">New Incident</h2>
        </div>
        <p className="text-sm text-slate-400">
          Submit the incident details. The agent will search historical memory for similar incidents and provide context-aware guidance.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Form */}
        <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-6">
          <h3 className="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wide">Incident Details</h3>
          <IncidentForm onSubmit={handleSubmit} loading={loading} />
        </div>

        {/* Right: Analysis */}
        <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-6">
          <h3 className="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wide">Agent Analysis</h3>
          {!result && !loading && (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <div className="w-16 h-16 rounded-2xl bg-slate-700/50 flex items-center justify-center mb-4">
                <AlertTriangle size={24} className="text-slate-500" />
              </div>
              <p className="text-slate-500 text-sm">Submit an incident to see the AI analysis and memory recall results.</p>
            </div>
          )}
          {loading && (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 flex items-center justify-center mb-4 animate-pulse">
                <span className="text-3xl">🧠</span>
              </div>
              <p className="text-slate-400 text-sm font-medium">Searching memory &amp; analyzing...</p>
              <p className="text-slate-500 text-xs mt-1">Querying Hindsight and calling Groq LLM</p>
            </div>
          )}
          {result && <AnalysisPanel result={result} />}
        </div>
      </div>
    </main>
  )
}
