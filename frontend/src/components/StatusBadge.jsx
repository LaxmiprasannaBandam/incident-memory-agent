import React from 'react'

const SEVERITY_STYLES = {
  critical: 'bg-red-500/20 text-red-400 border-red-500/30',
  high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  low: 'bg-green-500/20 text-green-400 border-green-500/30',
}

const ENV_STYLES = {
  production: 'bg-red-500/10 text-red-300 border-red-500/20',
  staging: 'bg-blue-500/10 text-blue-300 border-blue-500/20',
  dev: 'bg-slate-500/10 text-slate-300 border-slate-500/20',
}

export default function StatusBadge({ severity, environment }) {
  return (
    <div className="flex gap-2 flex-wrap">
      {severity && (
        <span className={`text-xs font-semibold px-2 py-1 rounded-full border ${SEVERITY_STYLES[severity] || SEVERITY_STYLES.medium}`}>
          {severity.toUpperCase()}
        </span>
      )}
      {environment && (
        <span className={`text-xs font-semibold px-2 py-1 rounded-full border ${ENV_STYLES[environment] || ENV_STYLES.dev}`}>
          {environment}
        </span>
      )}
    </div>
  )
}
