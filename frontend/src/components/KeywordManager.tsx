import { useState } from 'react'
import { Keyword, createKeyword, deleteKeyword } from '../services/api'

interface KeywordManagerProps {
  keywords: Keyword[]
  onKeywordChange: () => void
  loading: boolean
}

export default function KeywordManager({ keywords, onKeywordChange, loading }: KeywordManagerProps) {
  const [newKeyword, setNewKeyword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newKeyword.trim() || submitting) return

    setSubmitting(true)
    setError(null)

    try {
      await createKeyword(newKeyword.trim())
      setNewKeyword('')
      onKeywordChange()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add keyword')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (keyword: Keyword) => {
    setDeletingId(keyword.id)
    setError(null)

    try {
      await deleteKeyword(keyword.keyword)
      onKeywordChange()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete keyword')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="bg-midnight-900/50 backdrop-blur-sm rounded-2xl border border-midnight-700 p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-accent-amber/20 rounded-xl flex items-center justify-center">
          <svg className="w-5 h-5 text-accent-amber" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
        </div>
        <div>
          <h2 className="text-lg font-semibold text-white">Your Keywords</h2>
          <p className="text-sm text-slate-400">Add keywords to personalize your news feed</p>
        </div>
      </div>

      {/* Add keyword form */}
      <form onSubmit={handleSubmit} className="flex gap-2 mb-4">
        <input
          type="text"
          value={newKeyword}
          onChange={(e) => setNewKeyword(e.target.value)}
          placeholder="Enter a keyword..."
          className="flex-1 bg-midnight-800 border border-midnight-600 rounded-xl px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-accent-cyan transition-colors"
          disabled={submitting}
        />
        <button
          type="submit"
          disabled={!newKeyword.trim() || submitting}
          className="px-5 py-2.5 bg-gradient-to-r from-accent-cyan to-accent-pink text-white font-medium rounded-xl transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            'Add'
          )}
        </button>
      </form>

      {error && (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Keywords list */}
      {loading ? (
        <div className="flex justify-center py-4">
          <div className="w-6 h-6 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin" />
        </div>
      ) : keywords.length === 0 ? (
        <p className="text-slate-500 text-sm text-center py-4">
          No keywords yet. Add some to see personalized news!
        </p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {keywords.map((keyword) => (
            <span
              key={keyword.id}
              className="inline-flex items-center gap-2 px-3 py-1.5 bg-midnight-800 border border-midnight-600 rounded-full text-sm text-slate-300"
            >
              {keyword.keyword}
              <button
                onClick={() => handleDelete(keyword)}
                disabled={deletingId === keyword.id}
                className="text-slate-500 hover:text-red-400 transition-colors disabled:opacity-50"
              >
                {deletingId === keyword.id ? (
                  <div className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin" />
                ) : (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                )}
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

