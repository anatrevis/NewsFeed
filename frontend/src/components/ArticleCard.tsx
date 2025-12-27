import { Link } from 'react-router-dom'
import { Article } from '../services/api'

interface ArticleCardProps {
  article: Article
}

export default function ArticleCard({ article }: ArticleCardProps) {
  const formattedDate = article.publishedAt
    ? new Date(article.publishedAt).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      })
    : null

  // Create URL-safe state for article detail
  const articleState = encodeURIComponent(JSON.stringify(article))

  return (
    <Link
      to={`/article?data=${articleState}`}
      className="group block bg-midnight-900/50 backdrop-blur-sm rounded-2xl border border-midnight-700 overflow-hidden hover:border-accent-cyan/50 transition-all duration-300"
    >
      {/* Image */}
      {article.urlToImage ? (
        <div className="aspect-video overflow-hidden">
          <img
            src={article.urlToImage}
            alt={article.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              e.currentTarget.style.display = 'none'
            }}
          />
        </div>
      ) : (
        <div className="aspect-video bg-gradient-to-br from-midnight-800 to-midnight-900 flex items-center justify-center">
          <svg className="w-12 h-12 text-midnight-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
        </div>
      )}

      {/* Content */}
      <div className="p-5">
        {/* Source and date */}
        <div className="flex items-center gap-2 mb-3">
          {article.source.name && (
            <span className="text-xs font-medium text-accent-cyan bg-accent-cyan/10 px-2 py-1 rounded-full">
              {article.source.name}
            </span>
          )}
          {formattedDate && (
            <span className="text-xs text-slate-500">{formattedDate}</span>
          )}
        </div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2 group-hover:text-accent-cyan transition-colors">
          {article.title}
        </h3>

        {/* Description */}
        {article.description && (
          <p className="text-sm text-slate-400 line-clamp-3 mb-4">
            {article.description}
          </p>
        )}

        {/* Author */}
        {article.author && (
          <p className="text-xs text-slate-500">
            By {article.author}
          </p>
        )}
      </div>
    </Link>
  )
}

