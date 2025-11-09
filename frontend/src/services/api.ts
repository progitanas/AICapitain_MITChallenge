import axios, { AxiosInstance } from 'axios'

// API configuration - Correspond à l'API existante
const API_BASE_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 60000, // Augmenté pour les calculs d'optimisation
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config: any) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: any) => Promise.reject(error)
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error: any) => {
    // Handle auth errors
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API Error type
export interface ApiError {
  message: string
  status: number
  details?: unknown
}

// Parse error response
export const parseApiError = (error: unknown): ApiError => {
  if (axios.isAxiosError(error)) {
    return {
      message: error.response?.data?.detail || error.message,
      status: error.response?.status || 500,
      details: error.response?.data,
    }
  }
  return {
    message: 'An unexpected error occurred',
    status: 500,
  }
}

// ============== Route Optimization API ==============

export interface OptimizationRequest {
  vessel: {
    mmsi: string
    imo: string
    name: string
    call_sign: string
    dimensions: {
      length_m: number
      beam_m: number
      draught_m: number
      depth_m: number
    }
    type_code: number
    latitude: number
    longitude: number
    sog_knots: number
    cog_degrees: number
    heading_degrees: number
    nav_status: number
    destination_port?: string
  }
  start_port_id: string
  end_port_id: string
  weight_time?: number
  weight_cost?: number
  weight_risk?: number
  fuel_price_per_ton?: number
  avoid_piracy_zones?: boolean
  avoid_weather_risks?: boolean
}

export interface OptimizedRoute {
  waypoints: Array<{
    id: string
    name: string
    lat: number
    lon: number
  }>
  metrics: {
    distance_nm: number
    time_hours: number
    fuel_tons: number
    cost_usd: number
    risk_score: number
  }
  blockages: Array<{
    chokepoint: string
    risk_level: string
    recommendation: string
  }>
  generated_at: string
}

export const optimizeRoute = async (request: OptimizationRequest): Promise<OptimizedRoute> => {
  const response = await apiClient.post<OptimizedRoute>('/route/optimize', request)
  return response.data
}

export const getAlternativeRoutes = async (start: string, end: string, numAlternatives = 3) => {
  const response = await apiClient.get(`/route/alternatives`, {
    params: { start, end, num_alternatives: numAlternatives },
  })
  return response.data
}

// ============== Voyage & Monitoring API ==============

export interface VoyageRegisterRequest {
  vessel: OptimizationRequest['vessel']
  start_port: string
  end_port: string
}

export const registerVoyage = async (request: VoyageRegisterRequest) => {
  const response = await apiClient.post('/voyage/register', request)
  return response.data
}

export interface VesselPositionUpdate {
  mmsi: string
  latitude: number
  longitude: number
  timestamp: string
}

export const updateVesselPosition = async (update: VesselPositionUpdate) => {
  const response = await apiClient.put('/vessel/position', update)
  return response.data
}

export const getVesselDeviations = async (mmsi: string) => {
  const response = await apiClient.get(`/vessel/${mmsi}/deviations`)
  return response.data
}

export const getFleetStatus = async () => {
  const response = await apiClient.get('/fleet/status')
  return response.data
}

// ============== Forecasting API ==============

export interface CongestionForecastRequest {
  port_id: string
  arrival_date: string
  vessel_type?: string
}

export const forecastCongestion = async (request: CongestionForecastRequest) => {
  const response = await apiClient.post('/forecast/congestion', request)
  return response.data
}

export const getPortForecast = async (portId: string, days = 7) => {
  const response = await apiClient.get(`/port/${portId}/forecast`, {
    params: { days },
  })
  return response.data
}

// ============== Health & Status ==============

export interface Waypoint {
  id: string
  name: string
  latitude: number
  longitude: number
  port_type: string
  capacity: number
}

export const getWaypoints = async (): Promise<Waypoint[]> => {
  try {
    const response = await apiClient.get<{ waypoints: Waypoint[] }>('/waypoints')
    return response.data.waypoints
  } catch (error) {
    console.error('Error fetching waypoints:', error)
    return []
  }
}

export const getHealthStatus = async () => {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error) {
    return { status: 'error', message: 'API unavailable' }
  }
}

export default apiClient
