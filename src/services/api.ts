const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  phone?: string
  is_admin: boolean
  is_active: boolean
  is_blocked: boolean
  created_at: string
}

export interface Service {
  id: number
  name: string
  description?: string
  category: string
  service_type: string
  price_from: number
  duration_minutes: number
  is_active: boolean
  created_at: string
}

export interface Stylist {
  id: number
  name: string
  email?: string
  phone?: string
  specialties?: string
  is_active: boolean
  created_at: string
}

export interface AvailabilitySlot {
  date: string
  time: string
  stylist_id: number
  stylist_name: string
  available: boolean
}

export interface AppointmentCreate {
  stylist_id: number
  service_id: number
  appointment_date: string
  additional_services?: number[]
  notes?: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  first_name: string
  last_name: string
  phone?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

class ApiService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token')
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    }
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    })

    if (!response.ok) {
      throw new Error('Login failed')
    }

    const data = await response.json()
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    return data
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    })

    if (!response.ok) {
      throw new Error('Registration failed')
    }

    const data = await response.json()
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    return data
  }

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to get current user')
    }

    return response.json()
  }

  async getServices(category?: string, serviceType?: string): Promise<Service[]> {
    const params = new URLSearchParams()
    if (category) params.append('category', category)
    if (serviceType) params.append('service_type', serviceType)
    
    const response = await fetch(`${API_BASE_URL}/api/services?${params}`)
    
    if (!response.ok) {
      throw new Error('Failed to fetch services')
    }

    return response.json()
  }

  async getAvailability(date: string, serviceId: number): Promise<AvailabilitySlot[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/appointments/availability?date=${date}&service_id=${serviceId}`
    )

    if (!response.ok) {
      throw new Error('Failed to fetch availability')
    }

    return response.json()
  }

  async createAppointment(appointmentData: AppointmentCreate): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/appointments/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(appointmentData)
    })

    if (!response.ok) {
      throw new Error('Failed to create appointment')
    }

    return response.json()
  }

  async getMyAppointments(): Promise<any[]> {
    const response = await fetch(`${API_BASE_URL}/api/appointments/my-appointments`, {
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to fetch appointments')
    }

    return response.json()
  }

  async cancelAppointment(appointmentId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/appointments/${appointmentId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to cancel appointment')
    }
  }

  logout(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  }

  getCurrentUserFromStorage(): User | null {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  }
}

export const apiService = new ApiService()
