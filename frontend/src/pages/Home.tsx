import { useState, useEffect, useCallback } from 'react'
import KeywordManager from '../components/KeywordManager'
import ArticleCard from '../components/ArticleCard'
import { fetchKeywords, fetchArticles, Keyword, Article } from '../services/api'

type SortOption = 'publishedAt' | 'relevancy' | 'popularity'

const sortOptions: { value: SortOption; label: string; icon: string }[] = [
  { value: 'publishedAt', label: 'Latest', icon: '🕐' },
  { value: 'relevancy', label: 'Most Relevant', icon: '🎯' },
]

export default function Home() {
  const [keywords, setKeywords] = useState<Keyword[]>([])
  const [articles, setArticles] = useState<Article[]>([])
  const [keywordsLoading, setKeywordsLoading] = useState(true)
  const [articlesLoading, setArticlesLoading] = useState(false)
  const [articlesError, setArticlesError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [totalResults, setTotalResults] = useState(0)
  const [sortBy, setSortBy] = useState<SortOption>('publishedAt')
  const pageSize = 12

  const loadKeywords = useCallback(async () => {
    setKeywordsLoading(true)
    try {
      const data = await fetchKeywords()
      setKeywords(data.keywords)
    } catch (err) {
      console.error('Failed to load keywords:', err)
    } finally {
      setKeywordsLoading(false)
    }
  }, [])

  const loadArticles = useCallback(async () => {
    if (keywords.length === 0) {
      setArticles([])
      setTotalResults(0)
      return
    }

    setArticlesLoading(true)
    setArticlesError(null)

    try {
      const data = await fetchArticles(page, pageSize, sortBy)
      setArticles(data.articles)
      setTotalResults(data.totalResults)
    } catch (err) {
      setArticlesError(err instanceof Error ? err.message : 'Failed to load articles')
      setArticles([])
    } finally {
      setArticlesLoading(false)
    }
  }, [keywords.length, page, sortBy])

  // Load keywords on mount
  useEffect(() => {
    loadKeywords()
  }, [loadKeywords])

  // Load articles when keywords change
  useEffect(() => {
    if (!keywordsLoading) {
      loadArticles()
    }
  }, [keywordsLoading, loadArticles])

  const handleKeywordChange = () => {
    loadKeywords()
    setPage(1)
  }

  const handleSortChange = (newSort: SortOption) => {
    setSortBy(newSort)
    setPage(1)
  }

  const totalPages = Math.ceil(totalResults / pageSize)

  return (
    <div className="space-y-8">
      {/* Keywords section */}
      <KeywordManager
        keywords={keywords}
        onKeywordChange={handleKeywordChange}
        loading={keywordsLoading}
      />

      {/* Articles section */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white">Your News Feed</h2>
            <p className="text-slate-400 mt-1">
              {totalResults > 0
                ? `${totalResults.toLocaleString()} articles found`
                : 'Add keywords to see personalized news'}
            </p>
          </div>

          {/* Sort and Refresh controls */}
          {keywords.length > 0 && (
            <div className="flex items-center gap-3">
              {/* Sort dropdown */}
              <div className="relative">
                <select
                  value={sortBy}
                  onChange={(e) => handleSortChange(e.target.value as SortOption)}
                  disabled={articlesLoading}
                  className="appearance-none bg-midnight-800 hover:bg-midnight-700 border border-midnight-600 rounded-xl pl-4 pr-10 py-2 text-sm text-slate-300 transition-colors disabled:opacity-50 cursor-pointer focus:outline-none focus:border-accent-cyan"
                >
                  {sortOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.icon} {option.label}
                    </option>
                  ))}
                </select>
                <svg
                  className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>

              {/* Refresh button */}
              <button
                onClick={loadArticles}
                disabled={articlesLoading}
                className="flex items-center gap-2 px-4 py-2 bg-midnight-800 hover:bg-midnight-700 border border-midnight-600 rounded-xl text-sm text-slate-300 transition-colors disabled:opacity-50"
              >
                <svg
                  className={`w-4 h-4 ${articlesLoading ? 'animate-spin' : ''}`}
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
                Refresh
              </button>
            </div>
          )}
        </div>

        {/* Loading state */}
        {articlesLoading && (
          <div className="flex justify-center py-12">
            <div className="text-center">
              <div className="w-10 h-10 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-slate-400">Loading articles...</p>
            </div>
          </div>
        )}

        {/* Error state */}
        {articlesError && !articlesLoading && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 text-center">
            <div className="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <p className="text-red-400 mb-4">{articlesError}</p>
            <button
              onClick={loadArticles}
              className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-xl transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Empty state */}
        {!articlesLoading && !articlesError && keywords.length === 0 && (
          <div className="bg-midnight-900/50 border border-midnight-700 rounded-2xl p-12 text-center">
            <div className="w-16 h-16 bg-accent-cyan/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-accent-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">No keywords yet</h3>
            <p className="text-slate-400 max-w-md mx-auto">
              Add some keywords above to start seeing personalized news articles from sources around the web.
            </p>
          </div>
        )}

        {/* No results state */}
        {!articlesLoading && !articlesError && keywords.length > 0 && articles.length === 0 && (
          <div className="bg-midnight-900/50 border border-midnight-700 rounded-2xl p-12 text-center">
            <div className="w-16 h-16 bg-accent-amber/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-accent-amber" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">No articles found</h3>
            <p className="text-slate-400 max-w-md mx-auto">
              Try different keywords to find more articles.
            </p>
          </div>
        )}

        {/* Articles grid */}
        {!articlesLoading && !articlesError && articles.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {articles.map((article, index) => (
                <ArticleCard key={`${article.url}-${index}`} article={article} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-8">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 bg-midnight-800 hover:bg-midnight-700 border border-midnight-600 rounded-xl text-sm text-slate-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="text-slate-400 text-sm px-4">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-4 py-2 bg-midnight-800 hover:bg-midnight-700 border border-midnight-600 rounded-xl text-sm text-slate-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

