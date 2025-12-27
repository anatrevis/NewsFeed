import { useSearchParams, Link } from 'react-router-dom'
import { Article as ArticleType } from '../services/api'

export default function Article() {
  const [searchParams] = useSearchParams()
  
  // Parse article data from URL
  let article: ArticleType | null = null
  try {
    const data = searchParams.get('data')
    if (data) {
      article = JSON.parse(decodeURIComponent(data))
    }
  } catch (err) {
    console.error('Failed to parse article data:', err)
  }

  if (!article) {
    return (
      <div className="max-w-3xl mx-auto text-center py-12">
        <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-white mb-2">Article Not Found</h1>
        <p className="text-slate-400 mb-6">The article you're looking for doesn't exist or has been removed.</p>
        <Link
          to="/"
          className="inline-block px-6 py-3 bg-gradient-to-r from-accent-cyan to-accent-pink text-white font-medium rounded-xl transition-opacity hover:opacity-90"
        >
          Back to Home
        </Link>
      </div>
    )
  }

  const formattedDate = article.publishedAt
    ? new Date(article.publishedAt).toLocaleDateString('en-US', {
        weekday: 'long',
        month: 'long',
        day: 'numeric',
        year: 'numeric',
      })
    : null

  return (
    <div className="max-w-3xl mx-auto">
      {/* Back button */}
      <Link
        to="/"
        className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-8"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back to Feed
      </Link>

      {/* Article card */}
      <article className="bg-midnight-900/50 backdrop-blur-sm rounded-2xl border border-midnight-700 overflow-hidden">
        {/* Image */}
        {article.urlToImage && (
          <div className="aspect-video">
            <img
              src={article.urlToImage}
              alt={article.title}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
          </div>
        )}

        <div className="p-8">
          {/* Meta */}
          <div className="flex flex-wrap items-center gap-3 mb-4">
            {article.source.name && (
              <span className="text-sm font-medium text-accent-cyan bg-accent-cyan/10 px-3 py-1 rounded-full">
                {article.source.name}
              </span>
            )}
            {formattedDate && (
              <span className="text-sm text-slate-500">{formattedDate}</span>
            )}
          </div>

          {/* Title */}
          <h1 className="text-3xl font-bold text-white mb-4 leading-tight">
            {article.title}
          </h1>

          {/* Author */}
          {article.author && (
            <p className="text-slate-400 mb-6">
              By <span className="text-white">{article.author}</span>
            </p>
          )}

          {/* Description */}
          {article.description && (
            <div className="mb-6">
              <p className="text-lg text-slate-300 leading-relaxed">
                {article.description}
              </p>
            </div>
          )}

          {/* Content preview */}
          {article.content && (
            <div className="mb-8 p-6 bg-midnight-800/50 rounded-xl border border-midnight-700">
              <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">Preview</h2>
              <p className="text-slate-300 leading-relaxed">
                {article.content.replace(/\[\+\d+ chars\]$/, '')}
              </p>
            </div>
          )}

          {/* Read full article button */}
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-accent-cyan to-accent-pink text-white font-medium rounded-xl transition-opacity hover:opacity-90"
          >
            Read Full Article
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </article>
    </div>
  )
}

