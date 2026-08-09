import axios from 'axios'
import { auth } from './firebase'

export const api = axios.create({
  baseURL: '/api/v1',
})

// Attach the current Firebase ID token to every request.
api.interceptors.request.use(async (config) => {
  const user = auth.currentUser
  if (user) {
    const token = await user.getIdToken()
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// API types (mirror the backend schemas — will refine as pages are built).
export type AnalysisStatus = 'pending' | 'processing' | 'completed' | 'failed'
export type AnalysisType = 'text' | 'url' | 'image' | 'video' | 'voice'

export interface Analysis {
  id: string
  type: AnalysisType
  status: AnalysisStatus
  title?: string | null
  summary?: string | null
  credibility_score?: number | null
  input_payload?: Record<string, unknown> | null
  created_at: string
  claims?: Claim[]
}

export interface Claim {
  id: string
  claim_text: string
  status: string
  confidence: number
  position: number
  sources?: Source[]
  evidence?: Evidence[]
}

export interface Source {
  id: string
  url: string
  title?: string | null
}

export interface Evidence {
  id: string
  quote?: string | null
  url?: string | null
}

export interface MediaUploadResponse {
  path: string
  url: string
}
