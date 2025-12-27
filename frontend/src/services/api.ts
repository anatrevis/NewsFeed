const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function getAuthHeader(): HeadersInit {
  const token = localStorage.getItem('newsfeed_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

// Keyword types
export interface Keyword {
  id: string
  keyword: string
  created_at: string
}

export interface KeywordList {
  keywords: Keyword[]
  total: number
}

// Article types
export interface ArticleSource {
  id: string | null
  name: string | null
}

export interface Article {
  source: ArticleSource
  author: string | null
  title: string
  description: string | null
  url: string
  urlToImage: string | null
  publishedAt: string | null
  content: string | null
}

export interface ArticleList {
  articles: Article[]
  totalResults: number
  status: string
}

// Keywords API
export async function fetchKeywords(): Promise<KeywordList> {
  const response = await fetch(`${API_URL}/api/keywords`, {
    headers: getAuthHeader(),
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch keywords')
  }
  
  return response.json()
}

export async function createKeyword(keyword: string): Promise<Keyword> {
  const response = await fetch(`${API_URL}/api/keywords`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(),
    },
    body: JSON.stringify({ keyword }),
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || 'Failed to create keyword')
  }
  
  return response.json()
}

export async function deleteKeyword(keyword: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/keywords/${encodeURIComponent(keyword)}`, {
    method: 'DELETE',
    headers: getAuthHeader(),
  })
  
  if (!response.ok) {
    throw new Error('Failed to delete keyword')
  }
}

// Articles API
export async function fetchArticles(
  page: number = 1,
  pageSize: number = 20,
  sortBy: string = 'publishedAt'
): Promise<ArticleList> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
    sort_by: sortBy,
  })
  
  const response = await fetch(`${API_URL}/api/articles?${params}`, {
    headers: getAuthHeader(),
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || 'Failed to fetch articles')
  }
  
  return response.json()
}

