import { useAuth } from '../context/AuthContext'
import { Navigate } from 'react-router-dom'

export default function Login() {
  const { login, isAuthenticated } = useAuth()

  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-accent-cyan to-accent-pink rounded-2xl flex items-center justify-center shadow-lg shadow-accent-cyan/20">
            <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
          </div>
          <h1 className="text-4xl font-bold text-white mb-3">NewsFeed</h1>
          <p className="text-slate-400 text-lg">Your personalized news, curated by keywords</p>
        </div>

        <div className="bg-midnight-900/50 backdrop-blur-sm rounded-2xl p-8 border border-midnight-700 shadow-xl">
          <button
            onClick={login}
            className="w-full py-4 px-6 bg-gradient-to-r from-accent-cyan to-accent-pink hover:opacity-90 text-white font-semibold rounded-xl transition-all flex items-center justify-center gap-3 shadow-lg shadow-accent-cyan/20"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
            Sign in with Authentik
          </button>

          <div className="mt-6 text-center">
            <p className="text-slate-500 text-sm">
              Protected by OAuth 2.0 authentication
            </p>
          </div>
        </div>

        <div className="mt-8 text-center">
          <p className="text-slate-500 text-sm">
            New user? Sign up through Authentik to get started.
          </p>
        </div>
      </div>
    </div>
  )
}

