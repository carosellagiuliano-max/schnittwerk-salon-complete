const API_BASE_URL = 'http://localhost:8000'

export interface Profile {
  id: number
  tenant_id: string
  email: string
  role: string
  full_name?: string
  phone?: string
  is_active: boolean
  created_at: string
}

export interface Service {
  id: number
  tenant_id: string
  name: string
  duration_min: number
  price_cents: number
  active: boolean
  created_at: string
}

export interface Staff {
  id: number
  tenant_id: string
  name: string
  active: boolean
  image_url?: string
  created_at: string
}

export interface Booking {
  id: number
  tenant_id: string
  service_id: number
  staff_id: number
  customer_email: string
  start_at: string
  end_at: string
  status: string
  created_by?: string
  cancelled_by?: string
  created_at: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  full_name?: string
  phone?: string
  role?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  profile: Profile
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
    localStorage.setItem('profile', JSON.stringify(data.profile))
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
    localStorage.setItem('profile', JSON.stringify(data.profile))
    return data
  }

  async getCurrentProfile(): Promise<Profile> {
    const profileStr = localStorage.getItem('profile')
    if (!profileStr) {
      throw new Error('No profile found')
    }
    return JSON.parse(profileStr)
  }

  async getServices(): Promise<Service[]> {
    const response = await fetch(`${API_BASE_URL}/api/services`)
    
    if (!response.ok) {
      throw new Error('Failed to fetch services')
    }

    return response.json()
  }

  async getStaff(): Promise<Staff[]> {
    const response = await fetch(`${API_BASE_URL}/api/staff`)
    
    if (!response.ok) {
      throw new Error('Failed to fetch staff')
    }

    return response.json()
  }

  async getAvailability(serviceId: number, staffId: number, date: string): Promise<string[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/availability?service_id=${serviceId}&staff_id=${staffId}&date=${date}`
    )

    if (!response.ok) {
      throw new Error('Failed to fetch availability')
    }

    return response.json()
  }

  async createBooking(bookingData: any): Promise<Booking> {
    const response = await fetch(`${API_BASE_URL}/api/bookings`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(bookingData)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to create booking')
    }

    return response.json()
  }

  async getMyBookings(): Promise<Booking[]> {
    const response = await fetch(`${API_BASE_URL}/api/bookings/me`, {
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to fetch bookings')
    }

    return response.json()
  }

  async cancelBooking(bookingId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/bookings/${bookingId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to cancel booking')
    }
  }

  async getAdminServices(): Promise<Service[]> {
    const response = await fetch(`${API_BASE_URL}/api/admin/services`, {
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to fetch admin services')
    }

    return response.json()
  }

  async createService(serviceData: any): Promise<Service> {
    const response = await fetch(`${API_BASE_URL}/api/admin/services`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        name: serviceData.name,
        duration_min: parseInt(serviceData.duration) || 60,
        price_cents: Math.round((parseFloat(serviceData.price) || 0) * 100)
      })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to create service')
    }

    return response.json()
  }

  async updateService(serviceId: number, serviceData: any): Promise<Service> {
    const response = await fetch(`${API_BASE_URL}/api/admin/services/${serviceId}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        name: serviceData.name,
        duration_min: parseInt(serviceData.duration_min),
        price_cents: parseInt(serviceData.price_cents)
      })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to update service')
    }

    return response.json()
  }

  async deleteService(serviceId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/admin/services/${serviceId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to delete service')
    }
  }

  async getAdminStaff(): Promise<Staff[]> {
    const response = await fetch(`${API_BASE_URL}/api/admin/staff`, {
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to fetch admin staff')
    }

    return response.json()
  }

  async createStaff(staffData: any): Promise<Staff> {
    const response = await fetch(`${API_BASE_URL}/api/admin/staff`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(staffData)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to create staff')
    }

    return response.json()
  }

  async updateStaff(staffId: number, staffData: any): Promise<Staff> {
    const response = await fetch(`${API_BASE_URL}/api/admin/staff/${staffId}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(staffData)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to update staff')
    }

    return response.json()
  }

  async deleteStaff(staffId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/admin/staff/${staffId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to delete staff')
    }
  }

  async getStaffSchedules(staffId: number): Promise<any[]> {
    const response = await fetch(`${API_BASE_URL}/api/admin/staff/${staffId}/schedules`, {
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to fetch staff schedules')
    }

    return response.json()
  }

  async createStaffSchedule(staffId: number, scheduleData: any): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/admin/staff/${staffId}/schedules`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(scheduleData)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to create schedule')
    }

    return response.json()
  }

  async updateStaffSchedule(staffId: number, scheduleId: number, scheduleData: any): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/admin/staff/${staffId}/schedules/${scheduleId}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(scheduleData)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to update schedule')
    }

    return response.json()
  }

  async deleteStaffSchedule(staffId: number, scheduleId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/admin/staff/${staffId}/schedules/${scheduleId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to delete schedule')
    }
  }

  async getStaffTimeOff(staffId: number): Promise<any[]> {
    const response = await fetch(`${API_BASE_URL}/api/admin/staff/${staffId}/timeoff`, {
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to fetch staff time off')
    }

    return response.json()
  }

  async createStaffTimeOff(staffId: number, timeOffData: any): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/admin/staff/${staffId}/timeoff`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(timeOffData)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to create time off')
    }

    return response.json()
  }

  async updateStaffTimeOff(staffId: number, timeOffId: number, timeOffData: any): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/admin/staff/${staffId}/timeoff/${timeOffId}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(timeOffData)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to update time off')
    }

    return response.json()
  }

  async deleteStaffTimeOff(staffId: number, timeOffId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/admin/staff/${staffId}/timeoff/${timeOffId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to delete time off')
    }
  }

  async getAdminBookings(): Promise<Booking[]> {
    const response = await fetch(`${API_BASE_URL}/api/admin/bookings`, {
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to fetch admin bookings')
    }

    return response.json()
  }

  async adminCancelBooking(bookingId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/admin/bookings/${bookingId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to cancel booking')
    }
  }

  async getAdminCustomers(): Promise<Profile[]> {
    const response = await fetch(`${API_BASE_URL}/api/admin/customers`, {
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to fetch customers')
    }

    return response.json()
  }

  async banCustomer(email: string, reason?: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/admin/customers/ban`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ email, reason })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to ban customer')
    }

    return response.json()
  }

  async unbanCustomer(email: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/admin/customers/ban/${email}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to unban customer')
    }
  }

  async getTenantSettings(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/admin/tenant/settings`, {
      headers: this.getAuthHeaders()
    })

    if (!response.ok) {
      throw new Error('Failed to fetch tenant settings')
    }

    return response.json()
  }

  async updateTenantSettings(settings: any): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/admin/tenant/settings`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(settings)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to update tenant settings')
    }

    return response.json()
  }

  logout(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('profile')
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  }

  async getProducts(): Promise<any[]> {
    return []
  }

  async createProduct(productData: any): Promise<any> {
    throw new Error('Product management not yet implemented in multi-tenant backend')
  }

  async updateProduct(productId: number, productData: any): Promise<any> {
    throw new Error('Product management not yet implemented in multi-tenant backend')
  }

  async deleteProduct(productId: number): Promise<void> {
    throw new Error('Product management not yet implemented in multi-tenant backend')
  }

  getCurrentProfileFromStorage(): Profile | null {
    const profileStr = localStorage.getItem('profile')
    return profileStr ? JSON.parse(profileStr) : null
  }

  isAdmin(): boolean {
    const profile = this.getCurrentProfileFromStorage()
    return profile ? profile.role === 'owner' || profile.role === 'admin' : false
  }
}

export const apiService = new ApiService()
