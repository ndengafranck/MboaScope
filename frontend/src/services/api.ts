// The only module that talks to the backend. Endpoints: docs/api.md.
import type {
  InterpretResponse,
  InvestigationLog,
  InvestigationRequest,
  RainfallSeriesResponse,
  RegionsResponse,
  SpatialResponse,
  TrendsResponse,
} from '../types/api'

const BASE = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '') + '/api'

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(BASE + path, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    })
  } catch {
    throw new ApiError(0, 'The MboaScope server cannot be reached. Is the backend running?')
  }
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
    } catch {
      /* keep statusText */
    }
    throw new ApiError(res.status, detail)
  }
  return res.json() as Promise<T>
}

const post = <T>(path: string, body: unknown) => request<T>(path, { method: 'POST', body: JSON.stringify(body) })

export const api = {
  health: () => request<{ status: string; regions_with_data: string[]; is_mock: boolean }>('/health'),
  regions: () => request<RegionsResponse>('/regions'),
  rainfallSeries: (req: InvestigationRequest) => post<RainfallSeriesResponse>('/rainfall/series', req),
  trends: (req: InvestigationRequest) => post<TrendsResponse>('/analysis/trends', req),
  spatial: (req: InvestigationRequest) => post<SpatialResponse>('/analysis/spatial', req),
  history: (limit = 10) => request<InvestigationLog[]>(`/analysis/history?limit=${limit}`),
  interpret: (req: InvestigationRequest & { use_llm?: boolean }) => post<InterpretResponse>('/ai/interpret', req),
}
