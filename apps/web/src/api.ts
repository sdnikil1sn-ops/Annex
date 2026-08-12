import axios from 'axios'
import { auth } from './firebase'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api/v1',
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

// --- Types (mirror the backend schemas) ---

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

export interface CreateAnalysisInput {
  type: AnalysisType
  title?: string
  input_payload: Record<string, unknown>
}

// --- API calls ---

export async function createAnalysis(input: CreateAnalysisInput): Promise<Analysis> {
  const { data } = await api.post<Analysis>('/analyses', input)
  return data
}

export async function listAnalyses(): Promise<Analysis[]> {
  const { data } = await api.get<Analysis[] | { items: Analysis[] }>('/analyses')
  return Array.isArray(data) ? data : (data.items ?? [])
}

export async function getAnalysis(id: string): Promise<Analysis> {
  const { data } = await api.get<Analysis>(`/analyses/${id}`)
  return data
}

export async function uploadMedia(file: File): Promise<MediaUploadResponse> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<MediaUploadResponse>('/media/upload', form)
  return data
}
