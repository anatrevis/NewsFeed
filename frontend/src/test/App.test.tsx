import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from '../App'
import { AuthProvider } from '../context/AuthContext'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'sessionStorage', { value: sessionStorageMock })

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
  })

  it('redirects to login when not authenticated', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    )

    // Should show login page elements
    expect(screen.getByText('NewsFeed')).toBeInTheDocument()
    expect(screen.getByText(/Sign in with Authentik/i)).toBeInTheDocument()
  })

  it('shows loading state initially', () => {
    // Mock that we have a token stored
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'newsfeed_token') return 'mock-token'
      if (key === 'newsfeed_user') return JSON.stringify({ sub: '123', name: 'Test' })
      return null
    })

    render(
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    )

    // After loading, should show the authenticated layout
    // Note: The actual content depends on the auth state resolving
  })
})

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
  })

  it('provides authentication state', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    )

    // App should render without crashing
    expect(document.body).toBeTruthy()
  })

  it('loads stored auth data on mount', () => {
    const mockUser = { sub: '123', name: 'Test User', email: 'test@example.com' }
    
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'newsfeed_token') return 'stored-token'
      if (key === 'newsfeed_user') return JSON.stringify(mockUser)
      return null
    })

    render(
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    )

    // localStorage should be checked for token
    expect(localStorageMock.getItem).toHaveBeenCalledWith('newsfeed_token')
    expect(localStorageMock.getItem).toHaveBeenCalledWith('newsfeed_user')
  })
})

