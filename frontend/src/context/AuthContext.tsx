import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { loginUser, signupUser, logoutUser, UserInfo } from '../services/api'

interface AuthContextType {
  user: UserInfo | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  signup: (username: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for stored token on mount
    const storedToken = localStorage.getItem('newsfeed_token')
    const storedUser = localStorage.getItem('newsfeed_user')
    
    if (storedToken && storedUser) {
      try {
        setToken(storedToken)
        setUser(JSON.parse(storedUser))
      } catch {
        // Invalid stored data, clear it
        localStorage.removeItem('newsfeed_token')
        localStorage.removeItem('newsfeed_user')
      }
    }
    setLoading(false)
  }, [])

  const login = async (username: string, password: string) => {
    const response = await loginUser(username, password)
    
    // Store auth data
    localStorage.setItem('newsfeed_token', response.access_token)
    localStorage.setItem('newsfeed_user', JSON.stringify(response.user))
    setToken(response.access_token)
    setUser(response.user)
  }

  const signup = async (username: string, email: string, password: string) => {
    await signupUser(username, email, password)
    // Don't auto-login after signup - let user login manually
  }

  const logout = async () => {
    // Call backend to revoke token
    await logoutUser()
    
    // Clear local state
    localStorage.removeItem('newsfeed_token')
    localStorage.removeItem('newsfeed_user')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        loading,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
