const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function getAuthHeader(): HeadersInit {
  const token = localStorage.getItem('newsfeed_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

// Auth types
export interface UserInfo {
  sub: string
  email?: string
  name?: string
  preferred_username?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

export interface SignupResponse {
  message: string
  username: string
}

// Auth API
export async function loginUser(username: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Login failed' }))
    throw new Error(error.detail || 'Invalid username or password')
  }
  
  return response.json()
}

export async function signupUser(
  username: string,
  email: string,
  password: string
): Promise<SignupResponse> {
  const response = await fetch(`${API_URL}/api/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, email, password }),
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Signup failed' }))
    throw new Error(error.detail || 'Failed to create account')
  }
  
  return response.json()
}

export async function logoutUser(): Promise<void> {
  const token = localStorage.getItem('newsfeed_token')
  
  await fetch(`${API_URL}/api/auth/logout`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  }).catch(() => {
    // Ignore logout errors - we still want to clear local state
  })
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
  sortBy: string = 'publishedAt',
  language: string = 'en',
  matchMode: string = 'any'
): Promise<ArticleList> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
    sort_by: sortBy,
    language: language,
    match_mode: matchMode,
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

// Summarize types
export interface SummarizeStatus {
  enabled: boolean
  message: string | null
}

export interface ArticleForSummary {
  title: string
  description: string | null
  source: string | null
}

export interface SummarizeResponse {
  summary: string
}

// Summarize API
export async function fetchSummarizeStatus(): Promise<SummarizeStatus> {
  const response = await fetch(`${API_URL}/api/summarize/status`, {
    headers: getAuthHeader(),
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch summarize status')
  }
  
  return response.json()
}

export async function summarizeArticles(articles: Article[]): Promise<SummarizeResponse> {
  const articlesForSummary: ArticleForSummary[] = articles.map((art) => ({
    title: art.title,
    description: art.description,
    source: art.source?.name || null,
  }))
  
  const response = await fetch(`${API_URL}/api/summarize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(),
    },
    body: JSON.stringify({ articles: articlesForSummary }),
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Summarization failed' }))
    throw new Error(error.detail || 'Failed to summarize articles')
  }
  
  return response.json()
}

