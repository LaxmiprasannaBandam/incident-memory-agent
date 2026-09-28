import React from 'react'
import { Routes, Route } from 'react-router-dom'
import NewIncident from './pages/NewIncident'
import ResolveIncident from './pages/ResolveIncident'
import { Brain } from 'lucide-react'

export default function App() {
  return (
    <div className="min-h-screen bg-slate-900">
      {/* Navigation */}
      <nav className="border-b border-slate-700 bg-slate-900/95 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center gap-3">
          <div className="flex items-center gap-2 text-indigo-400">
            <Brain size={28} />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">
              Incident Memory Agent
            </h1>
            <p className="text-xs text-slate-400">Powered by Hindsight persistent memory</p>
          </div>
        </div>
      </nav>

      {/* Pages */}
      <Routes>
        <Route path="/" element={<NewIncident />} />
        <Route path="/resolve/:incidentId" element={<ResolveIncident />} />
      </Routes>
    </div>
  )
}
