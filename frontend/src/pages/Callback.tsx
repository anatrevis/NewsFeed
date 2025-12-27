import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Callback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { handleCallback } = useAuth()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const code = searchParams.get('code')
    const errorParam = searchParams.get('error')
    const errorDescription = searchParams.get('error_description')
    
    if (errorParam) {
      setError(errorDescription || errorParam)
      return
    }
    
    if (!code) {
      setError('No authorization code received')
      return
    }

    async function completeAuth() {
      try {
        await handleCallback(code!)
        navigate('/', { replace: true })
      } catch (err) {
        console.error('Auth callback error:', err)
        setError(err instanceof Error ? err.message : 'Failed to complete authentication')
      }
    }

    completeAuth()
  }, [searchParams, handleCallback, navigate])

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-midnight-900/50 backdrop-blur-sm p-8 rounded-2xl max-w-md text-center border border-midnight-700">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-white mb-2">Authentication Failed</h2>
          <p className="text-red-400 mb-6">{error}</p>
          <a 
            href="/login" 
            className="inline-block bg-gradient-to-r from-accent-cyan to-accent-pink text-white px-6 py-3 rounded-xl font-medium transition-opacity hover:opacity-90"
          >
            Try Again
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin w-12 h-12 border-4 border-accent-cyan border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-slate-300 text-lg">Completing sign in...</p>
        <p className="text-slate-500 text-sm mt-2">Please wait while we verify your credentials</p>
      </div>
    </div>
  )
}

