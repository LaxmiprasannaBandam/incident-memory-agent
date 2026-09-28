import React, { useState } from 'react'
import { Brain, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react'

export default function MemoryRecall({ memoryRecall }) {
  const [expanded, setExpanded] = useState(true)

  if (!memoryRecall) return null

  if (!memoryRecall.found) {
    return (
      <div className="border border-slate-600/50 rounded-xl p-4 bg-slate-800/30">
        <div className="flex items-center gap-2 text-slate-400">
          <AlertCircle size={16} />
          <span className="text-sm font-medium">No similar historical incidents found in memory.</span>
        </div>
        <p className="text-xs text-slate-500 mt-1 ml-6">
          This is the first time a similar incident has been analyzed.
          After resolution, this experience will be stored for future reference.
        </p>
      </div>
    )
  }

  return (
    <div className="border border-amber-500/40 rounded-xl bg-amber-500/5 overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-amber-500/10 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-amber-500/20">
            <Brain size={16} className="text-amber-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-amber-400">Memory Recall</span>
              <span className="text-xs bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded-full font-medium">
                {memoryRecall.memories.length} historical incident{memoryRecall.memories.length !== 1 ? 's' : ''} found
              </span>
            </div>
            <p className="text-xs text-amber-300/70 mt-0.5">
              Hindsight retrieved relevant past incidents. The AI used this context in its analysis.
            </p>
          </div>
        </div>
        {expanded ? (
          <ChevronUp size={16} className="text-amber-400 flex-shrink-0" />
        ) : (
          <ChevronDown size={16} className="text-amber-400 flex-shrink-0" />
        )}
      </button>

      {/* Memory cards */}
      {expanded && (
        <div className="px-4 pb-4 space-y-3">
          {memoryRecall.memories.map((memory, index) => (
            <div key={index} className="bg-slate-900/60 rounded-lg p-4 border border-amber-500/20">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-semibold text-amber-400">Historical Memory #{index + 1}</span>
              </div>
              <pre className="text-xs text-slate-300 whitespace-pre-wrap font-mono leading-relaxed overflow-auto max-h-64">
                {memory.text}
              </pre>
              {memory.relevance_note && (
                <p className="text-xs text-amber-300/60 mt-2 italic border-t border-amber-500/20 pt-2">
                  {memory.relevance_note}
                </p>
              )}
            </div>
          ))}

          <div className="text-xs text-slate-500 mt-2">
            Recall query used: <code className="text-slate-400 bg-slate-800 px-1 py-0.5 rounded">{memoryRecall.recall_query_used}</code>
          </div>
        </div>
      )}
    </div>
  )
}
