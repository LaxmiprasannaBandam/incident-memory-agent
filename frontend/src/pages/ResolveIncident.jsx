import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { CheckCircle, ArrowLeft, Brain } from 'lucide-react'
import ResolutionForm from '../components/ResolutionForm'
import StatusBadge from '../components/StatusBadge'
import { resolveIncident, getIncident } from '../api'

export default function ResolveIncident() {
  const { incidentId } = useParams()
  const navigate = useNavigate()
  const [incident, setIncident] = useState(null)
  const [loading, setLoading] = useState(false)
  const [resolved, setResolved] = useState(false)
  const [resolveResult, setResolveResult] = useState(null)

  useEffect(() => {
    getIncident(incidentId)
      .then(res => setIncident(res.data))
      .catch(() => toast.error('Could not load incident details'))
  }, [incidentId])

  const handleResolve = async (formData) => {
    setLoading(true)
    try {
      const response = await resolveIncident(incidentId, formData)
      setResolveResult(response.data)
      setResolved(true)
      toast.success('Experience stored in Hindsight memory!', { icon: '🧠' })
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Failed to record resolution'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-200 transition-colors mb-6"
      >
        <ArrowLeft size={14} /> Back to New Incident
      </button>

      {incident && (
        <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-5 mb-6">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-white mb-1">{incident.request?.title}</h2>
              <p className="text-sm text-slate-400">{incident.request?.service}</p>
            </div>
            <StatusBadge severity={incident.request?.severity} environment={incident.request?.environment} />
          </div>
        </div>
      )}

      {!resolved ? (
        <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-6">
          <div className="mb-5">
            <h3 className="text-base font-bold text-white mb-1">Record Resolution</h3>
            <p className="text-sm text-slate-400">
              Enter the actual root cause and fix. This experience will be stored in Hindsight
              and used to help resolve similar incidents in the future.
            </p>
          </div>
          <ResolutionForm onSubmit={handleResolve} loading={loading} />
        </div>
      ) : (
        <div className="bg-green-500/5 border border-green-500/30 rounded-2xl p-8 text-center">
          <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-4">
            <Brain size={28} className="text-green-400" />
          </div>
          <CheckCircle size={20} className="text-green-400 mx-auto mb-2" />
          <h3 className="text-lg font-bold text-white mb-2">Experience Stored in Memory</h3>
          <p className="text-sm text-slate-300 mb-1">{resolveResult?.message}</p>
          <p className="text-xs text-slate-500 mt-3">
            Memory ID: <code className="text-slate-400">{resolveResult?.document_id}</code>
          </p>
          <button
            onClick={() => navigate('/')}
            className="mt-6 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold py-2.5 px-6 rounded-xl transition-colors"
          >
            Analyze Another Incident
          </button>
        </div>
      )}
    </main>
  )
}
