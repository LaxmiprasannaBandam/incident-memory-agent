import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
})

export const analyzeIncident = (data) => api.post('/incidents/analyze', data)
export const resolveIncident = (incidentId, data) => api.post(`/incidents/${incidentId}/resolve`, data)
export const getIncident = (incidentId) => api.get(`/incidents/${incidentId}`)
export const checkHealth = () => api.get('/health')
