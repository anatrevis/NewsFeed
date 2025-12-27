import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface User {
  sub: string
  email?: string
  name?: string
  preferred_username?: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  login: () => void
  logout: () => void
  handleCallback: (code: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

const AUTHENTIK_URL = import.meta.env.VITE_AUTHENTIK_URL || 'http://localhost:9000'
const CLIENT_ID = import.meta.env.VITE_AUTHENTIK_CLIENT_ID || 'newsfeed-app'
const REDIRECT_URI = `${window.location.origin}/callback`

// PKCE helper functions
function generateCodeVerifier(): string {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return btoa(String.fromCharCode(...array))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '')
}

async function generateCodeChallenge(verifier: string): Promise<string> {
  const encoder = new TextEncoder()
  const data = encoder.encode(verifier)
  const hash = await crypto.subtle.digest('SHA-256', data)
  return btoa(String.fromCharCode(...new Uint8Array(hash)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '')
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for stored token on mount
    const storedToken = localStorage.getItem('newsfeed_token')
    const storedUser = localStorage.getItem('newsfeed_user')
    
    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
    }
    setLoading(false)
  }, [])

  const login = async () => {
    // Generate PKCE code verifier and challenge
    const codeVerifier = generateCodeVerifier()
    const codeChallenge = await generateCodeChallenge(codeVerifier)
    
    // Store code verifier for later use
    sessionStorage.setItem('pkce_code_verifier', codeVerifier)
    
    // Redirect to Authentik authorization endpoint
    const authUrl = new URL(`${AUTHENTIK_URL}/application/o/authorize/`)
    authUrl.searchParams.set('response_type', 'code')
    authUrl.searchParams.set('client_id', CLIENT_ID)
    authUrl.searchParams.set('redirect_uri', REDIRECT_URI)
    authUrl.searchParams.set('scope', 'openid email profile')
    authUrl.searchParams.set('state', crypto.randomUUID())
    authUrl.searchParams.set('code_challenge', codeChallenge)
    authUrl.searchParams.set('code_challenge_method', 'S256')
    
    window.location.href = authUrl.toString()
  }

  const handleCallback = async (code: string) => {
    const codeVerifier = sessionStorage.getItem('pkce_code_verifier')
    
    if (!codeVerifier) {
      throw new Error('No code verifier found. Please try logging in again.')
    }
    
    // Exchange code for token directly with Authentik (CORS supported since 2021.4)
    const response = await fetch(`${AUTHENTIK_URL}/application/o/token/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        client_id: CLIENT_ID,
        code: code,
        redirect_uri: REDIRECT_URI,
        code_verifier: codeVerifier,
      }),
    })
    
    if (!response.ok) {
      const error = await response.text()
      console.error('Token exchange failed:', error)
      throw new Error('Failed to exchange code for token')
    }
    
    const tokenData = await response.json()
    const accessToken = tokenData.access_token
    
    // Fetch user info directly from Authentik
    const userResponse = await fetch(`${AUTHENTIK_URL}/application/o/userinfo/`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    })
    
    if (!userResponse.ok) {
      throw new Error('Failed to fetch user info')
    }
    
    const userData = await userResponse.json()
    
    // Store auth data
    localStorage.setItem('newsfeed_token', accessToken)
    localStorage.setItem('newsfeed_user', JSON.stringify(userData))
    setToken(accessToken)
    setUser(userData)
    
    // Clean up
    sessionStorage.removeItem('pkce_code_verifier')
  }

  const logout = () => {
    localStorage.removeItem('newsfeed_token')
    localStorage.removeItem('newsfeed_user')
    setToken(null)
    setUser(null)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        loading,
        login,
        logout,
        handleCallback,
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

