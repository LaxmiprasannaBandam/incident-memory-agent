import React from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle, Search, Lightbulb, Wrench, ArrowRight, Sparkles } from 'lucide-react'
import MemoryRecall from './MemoryRecall'
import StatusBadge from './StatusBadge'

function Section({ icon, title, items, color = 'indigo' }) {
  const colorMap = {
    indigo: 'text-indigo-400',
    yellow: 'text-yellow-400',
    green: 'text-green-400',
  }
  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <span className={colorMap[color]}>{icon}</span>
        <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
      </div>
      <ol className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className="flex gap-3 text-sm text-slate-300">
            <span className={`flex-shrink-0 w-5 h-5 rounded-full text-xs font-bold flex items-center justify-center mt-0.5 ${
              color === 'green' ? 'bg-green-500/20 text-green-400' :
              color === 'yellow' ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-indigo-500/20 text-indigo-400'
            }`}>{i + 1}</span>
            <span className="leading-relaxed">{item}</span>
          </li>
        ))}
      </ol>
    </div>
  )
}

export default function AnalysisPanel({ result }) {
  const navigate = useNavigate()
  const { incident_id, analysis, memory_recall } = result

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <CheckCircle size={16} className="text-green-400" />
            <span className="text-sm font-semibold text-green-400">Analysis Complete</span>
          </div>
          <p className="text-xs text-slate-400">Incident ID: <code className="text-slate-300">{incident_id}</code></p>
        </div>
        {analysis.memory_influenced && (
          <div className="flex items-center gap-1.5 bg-amber-500/10 border border-amber-500/30 rounded-full px-3 py-1">
            <Sparkles size={12} className="text-amber-400" />
            <span className="text-xs font-semibold text-amber-400">Memory-informed</span>
          </div>
        )}
      </div>

      {/* Memory Recall — shown first, prominently */}
      <MemoryRecall memoryRecall={memory_recall} />

      {/* AI Summary */}
      <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
        <p className="text-sm text-slate-200 leading-relaxed">{analysis.summary}</p>
      </div>

      {/* Investigation Steps */}
      {analysis.investigation_steps?.length > 0 && (
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
          <Section
            icon={<Search size={16} />}
            title="Investigation Steps"
            items={analysis.investigation_steps}
            color="indigo"
          />
        </div>
      )}

      {/* Possible Causes */}
      {analysis.possible_causes?.length > 0 && (
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
          <Section
            icon={<Lightbulb size={16} />}
            title="Possible Causes"
            items={analysis.possible_causes}
            color="yellow"
          />
        </div>
      )}

      {/* Recommended Actions */}
      {analysis.recommended_actions?.length > 0 && (
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
          <Section
            icon={<Wrench size={16} />}
            title="Recommended Actions"
            items={analysis.recommended_actions}
            color="green"
          />
        </div>
      )}

      {/* Record Resolution CTA */}
      <button
        onClick={() => navigate(`/resolve/${incident_id}`)}
        className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 px-4 rounded-xl transition-colors"
      >
        Record Resolution & Store Memory
        <ArrowRight size={16} />
      </button>
    </div>
  )
}
