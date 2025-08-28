import React, { createContext, useContext, useState, useEffect } from 'react'
import { apiService, Profile, LoginCredentials, RegisterData } from '@/services/api'

interface AuthContextType {
  profile: Profile | null
  isAuthenticated: boolean
  isAdmin: boolean
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const initAuth = async () => {
      if (apiService.isAuthenticated()) {
        try {
          const currentProfile = await apiService.getCurrentProfile()
          setProfile(currentProfile)
        } catch (error) {
          apiService.logout()
        }
      }
      setIsLoading(false)
    }

    initAuth()
  }, [])

  const login = async (credentials: LoginCredentials) => {
    const response = await apiService.login(credentials)
    setProfile(response.profile)
  }

  const register = async (userData: RegisterData) => {
    const response = await apiService.register(userData)
    setProfile(response.profile)
  }

  const logout = () => {
    apiService.logout()
    setProfile(null)
  }

  const value = {
    profile,
    isAuthenticated: !!profile,
    isAdmin: profile ? (profile.role === 'owner' || profile.role === 'admin') : false,
    isLoading,
    login,
    register,
    logout
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
