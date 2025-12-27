import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { Navigate, Link, useNavigate } from 'react-router-dom'

export default function Signup() {
  const { isAuthenticated, signup } = useAuth()
  const navigate = useNavigate()
  
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  const validateForm = (): string | null => {
    if (!username.trim()) {
      return 'Username is required'
    }
    if (username.length < 3) {
      return 'Username must be at least 3 characters'
    }
    if (username.length > 50) {
      return 'Username must be less than 50 characters'
    }
    if (!/^[a-z0-9]+$/.test(username)) {
      return 'Username must contain only lowercase letters and numbers'
    }
    if (!email.trim()) {
      return 'Email is required'
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return 'Please enter a valid email address'
    }
    if (!password) {
      return 'Password is required'
    }
    if (password.length < 8) {
      return 'Password must be at least 8 characters'
    }
    if (password !== confirmPassword) {
      return 'Passwords do not match'
    }
    return null
  }

  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Auto-convert to lowercase and remove invalid characters
    const value = e.target.value.toLowerCase().replace(/[^a-z0-9]/g, '')
    setUsername(value)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const validationError = validateForm()
    if (validationError) {
      setError(validationError)
      return
    }
    
    setError(null)
    setLoading(true)
    
    try {
      await signup(username.trim(), email.trim().toLowerCase(), password)
      setSuccess(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create account')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <div className="bg-midnight-900/50 backdrop-blur-sm rounded-2xl p-8 border border-midnight-700 shadow-xl text-center">
            <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Account Created!</h2>
            <p className="text-slate-400 mb-6">
              Your account has been created successfully. You can now sign in with your credentials.
            </p>
            <button
              onClick={() => navigate('/login')}
              className="w-full py-4 px-6 bg-gradient-to-r from-accent-cyan to-accent-pink hover:opacity-90 text-white font-semibold rounded-xl transition-all shadow-lg shadow-accent-cyan/20"
            >
              Go to Sign In
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-accent-cyan to-accent-pink rounded-2xl flex items-center justify-center shadow-lg shadow-accent-cyan/20">
            <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
          </div>
          <h1 className="text-4xl font-bold text-white mb-3">NewsFeed</h1>
          <p className="text-slate-400 text-lg">Create your account</p>
        </div>

        {/* Signup Form */}
        <div className="bg-midnight-900/50 backdrop-blur-sm rounded-2xl p-8 border border-midnight-700 shadow-xl">
          <h2 className="text-xl font-semibold text-white mb-6 text-center">Sign up for NewsFeed</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Error Message */}
            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
                <div className="flex items-center gap-3">
                  <svg className="w-5 h-5 text-red-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <p className="text-red-400 text-sm">{error}</p>
                </div>
              </div>
            )}
            
            {/* Username Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-slate-300 mb-2">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={handleUsernameChange}
                disabled={loading}
                placeholder="Choose a username"
                className="w-full px-4 py-3 bg-midnight-800 border border-midnight-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-accent-cyan transition-colors disabled:opacity-50"
                autoComplete="username"
              />
              <p className="mt-1 text-xs text-slate-500">Lowercase letters and numbers only, 3-50 characters</p>
            </div>
            
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                placeholder="Enter your email"
                className="w-full px-4 py-3 bg-midnight-800 border border-midnight-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-accent-cyan transition-colors disabled:opacity-50"
                autoComplete="email"
              />
            </div>
            
            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                placeholder="Create a password"
                className="w-full px-4 py-3 bg-midnight-800 border border-midnight-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-accent-cyan transition-colors disabled:opacity-50"
                autoComplete="new-password"
              />
              <p className="mt-1 text-xs text-slate-500">Minimum 8 characters</p>
            </div>
            
            {/* Confirm Password Field */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-300 mb-2">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading}
                placeholder="Confirm your password"
                className="w-full px-4 py-3 bg-midnight-800 border border-midnight-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-accent-cyan transition-colors disabled:opacity-50"
                autoComplete="new-password"
              />
            </div>
            
            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 px-6 bg-gradient-to-r from-accent-cyan to-accent-pink hover:opacity-90 text-white font-semibold rounded-xl transition-all flex items-center justify-center gap-3 shadow-lg shadow-accent-cyan/20 disabled:opacity-50 disabled:cursor-not-allowed mt-6"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Creating account...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 7a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1V7z" />
                  </svg>
                  Create Account
                </>
              )}
            </button>
          </form>
          
          <div className="mt-6 text-center">
            <p className="text-slate-500 text-sm">
              Already have an account?{' '}
              <Link to="/login" className="text-accent-cyan hover:underline font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

