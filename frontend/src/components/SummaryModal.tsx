import { useState, useEffect } from 'react'
import { summarizeArticles, Article } from '../services/api'

interface SummaryModalProps {
  articles: Article[]
  isOpen: boolean
  onClose: () => void
}

/**
 * Renders text with basic markdown formatting (bold with **)
 */
function FormattedText({ text }: { text: string }) {
  // Split text by **bold** pattern and render with proper formatting
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  
  return (
    <>
      {parts.map((part, index) => {
        // Check if this part is bold (wrapped in **)
        if (part.startsWith('**') && part.endsWith('**')) {
          const boldText = part.slice(2, -2)
          return (
            <span key={index} className="font-semibold text-accent-cyan">
              {boldText}
            </span>
          )
        }
        return <span key={index}>{part}</span>
      })}
    </>
  )
}

export default function SummaryModal({ articles, isOpen, onClose }: SummaryModalProps) {
  const [summary, setSummary] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen && articles.length > 0) {
      generateSummary()
    }
    // Reset state when modal is closed
    if (!isOpen) {
      setSummary(null)
      setError(null)
    }
  }, [isOpen])

  const generateSummary = async () => {
    setLoading(true)
    setError(null)
    setSummary(null)

    try {
      const response = await summarizeArticles(articles)
      setSummary(response.summary)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate summary')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-2xl max-h-[80vh] mx-4 bg-midnight-900 border border-midnight-700 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-midnight-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-accent-cyan to-accent-pink rounded-xl flex items-center justify-center">
              <svg
                className="w-5 h-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">AI Summary</h2>
              <p className="text-sm text-slate-400">
                Summarizing {articles.length} article{articles.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white hover:bg-midnight-800 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-6 max-h-[60vh] overflow-y-auto">
          {/* Loading state */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="w-12 h-12 border-3 border-accent-cyan border-t-transparent rounded-full animate-spin mb-4" />
              <p className="text-slate-400">Generating AI summary...</p>
              <p className="text-sm text-slate-500 mt-2">This may take a few seconds</p>
            </div>
          )}

          {/* Error state */}
          {error && !loading && (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-8 h-8 text-red-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
              <p className="text-red-400 mb-4">{error}</p>
              <button
                onClick={generateSummary}
                className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-xl transition-colors"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Summary content */}
          {summary && !loading && (
            <div className="prose prose-invert max-w-none">
              <div className="text-slate-300 leading-relaxed">
                {summary.split('\n\n').map((paragraph, pIndex) => (
                  <p key={pIndex} className="mb-4 last:mb-0">
                    <FormattedText text={paragraph} />
                  </p>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        {summary && !loading && (
          <div className="px-6 py-4 border-t border-midnight-700 bg-midnight-800/50">
            <div className="flex items-center justify-between">
              <p className="text-xs text-slate-500">
                Powered by OpenAI
              </p>
              <button
                onClick={generateSummary}
                className="flex items-center gap-2 px-4 py-2 text-sm text-slate-300 hover:text-white hover:bg-midnight-700 rounded-lg transition-colors"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                Regenerate
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

