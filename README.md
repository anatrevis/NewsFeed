# NewsFeed - Personalized News Application

A full-stack news aggregator where authenticated users save keyword preferences and view personalized articles from [News API](https://newsapi.org).

## Features

- **User Authentication**: Custom login/signup UI with Authentik backend
- **Keyword Management**: Save and delete personal keyword preferences
- **Personalized Feed**: View articles filtered by your keywords with OR/AND matching
- **Article Sorting & Filtering**: Sort by date/relevancy, filter by 13 languages
- **Article Details**: Click into articles for more detail with links to full articles
- **Responsive UI**: Modern React interface with Tailwind CSS
- **Structured Logging**: Configurable log levels with dev/production formats

### Bonus Feature: AI-Powered Summarization

- **AI Summary**: Generate intelligent summaries of your news feed using OpenAI
- Click the "AI Summary" button to get a concise overview of all visible articles
- Highlights key themes, events, and takeaways across multiple stories
- Requires an OpenAI API key (optional - feature is disabled without it)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Authentication | Authentik (OAuth2/OIDC) |
| Database | PostgreSQL 15 |
| External API | [News API](https://newsapi.org) |
| AI Summarization | [OpenAI](https://openai.com) (optional) |
| Infrastructure | Docker Compose |
| Testing | Pytest, Vitest |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Docker Compose Network                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐                                           │
│  │    Frontend      │                                           │
│  │  React + TS      │                                           │
│  │  :3000           │                                           │
│  └────────┬─────────┘                                           │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   FastAPI Backend                         │   │
│  │                       :8000                               │   │
│  └─────┬─────────────┬─────────────┬─────────────┬──────────┘   │
│        │             │             │             │               │
│        ▼             ▼             ▼             ▼               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │PostgreSQL│  │ Authentik│  │ News API │  │  OpenAI  │         │
│  │  :5432   │  │  :9000   │  │(External)│  │(External)│         │
│  │• newsfeed│  │OAuth2/JWT│  │          │  │ Optional │         │
│  │• authentik│ │          │  │          │  │          │         │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

> **Note:** The frontend communicates exclusively with the FastAPI backend. 
> Authentication is handled via custom login/signup forms that proxy requests 
> to Authentik through the backend, keeping all external service communication 
> server-side.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- News API key (get one free at https://newsapi.org/register)

### Setup

1. **Clone and configure**
   ```bash
   git clone https://github.com/anatrevis/NewsFeed.git
   cd NewsFeed
   cp .env.example .env
   ```

2. **Configure environment variables** - Edit `.env`:

   **Required:**
   ```bash
   # Get your free API key at https://newsapi.org/register
   NEWS_API_KEY=your-actual-newsapi-key-here
   ```

   **Recommended (for security):**
   ```bash
   # Generate a random secret key:
   # openssl rand -hex 32
   # or: python -c "import secrets; print(secrets.token_hex(32))"
   AUTHENTIK_SECRET_KEY=your-generated-secret-key
   ```

   **Optional (for AI Summary feature):**
   ```bash
   # Get your API key at https://platform.openai.com/api-keys
   OPENAI_API_KEY=your-openai-api-key
   ```

3. **Build and start everything**
   ```bash
   docker compose up -d --build
   ```

4. **Wait for initialization** (~2-3 minutes on first run), then access:
   - **Frontend**: http://localhost:3000
   - **API Docs**: http://localhost:8000/docs  
   - **Authentik Admin**: http://localhost:9000

### Authentication

The application uses a **custom login/signup UI** with Authentik as the authentication backend. Users can self-register without needing admin access!

**Self-Registration:**
1. Go to: http://localhost:3000
2. Click "Sign up" on the login page
3. Create an account with username (lowercase letters/numbers only), email, and password
4. Login with your new credentials

**Username Requirements:**
- 3-50 characters
- Lowercase letters and numbers only (no spaces, uppercase, or special characters)

**Admin Access** (for managing users):
- Authentik Admin: http://localhost:9000
- Default credentials: `akadmin` / `admin123`

**What's auto-configured via Blueprints:**
- ✅ OAuth2 Provider (`NewsFeed Provider`)
- ✅ Application (`NewsFeed` with slug `newsfeed-app`)
- ✅ Enrollment flow for self-registration
- ✅ Client ID: `newsfeed-app` (public client)
- ✅ OpenID scopes: `openid`, `email`, `profile`

## How Keyword Filtering Works

1. **Add Keywords**: Users add keywords that matter to them (e.g., "python", "AI", "climate")

2. **Keyword Storage**: Keywords are stored in PostgreSQL, associated with the user's ID from Authentik

3. **Article Fetching**: When viewing the feed:
   - Backend retrieves user's keywords
   - Combines them with OR logic (e.g., `python OR AI OR climate`)
   - Sends query to News API's `/everything` endpoint
   - Returns matching articles from the last 30 days

4. **Results**: Users see articles from various sources matching their interests

5. **Match Mode**: Users can toggle between:
   - **Any Keyword (OR)**: Articles matching any of your keywords (broader results)
   - **All Keywords (AND)**: Articles containing all keywords (stricter, more relevant)

6. **Sorting**: Articles can be sorted by:
   - **Latest**: Most recent articles first (default)
   - **Most Relevant**: Articles most relevant to your keywords

7. **Language Filter**: Filter articles by 13 supported languages:
   - English, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Chinese, Arabic, Hebrew, Norwegian, Swedish

## Logging

The backend features structured logging with different formats for development and production:

### Development Mode (default)
Human-readable colored output:
```
2025-12-27 17:02:48 | INFO    | newsfeed.app.main | main.py:24 | NewsFeed API starting...
```

### Production Mode
JSON format for log aggregators (ELK, CloudWatch, etc.):
```json
{"timestamp": "2025-12-27T17:02:48Z", "level": "INFO", "logger": "newsfeed.app.main", "message": "..."}
```

### Configuration
Set in your `.env` file:
```bash
ENVIRONMENT=development  # or production
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

Use `DEBUG` for verbose output during development, `WARNING` or `ERROR` for production.

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/keywords` | Get user's saved keywords | Required |
| POST | `/api/keywords` | Add a keyword | Required |
| DELETE | `/api/keywords/{keyword}` | Remove a keyword | Required |
| GET | `/api/articles` | Get articles for user's keywords | Required |
| GET | `/api/summarize/status` | Check if AI summarization is available | Public |
| POST | `/api/summarize` | Generate AI summary of articles | Required |
| GET | `/health` | Health check | Public |

## Running Tests

### Via Docker (Recommended)

If you have the Docker environment running, tests run inside the containers with all dependencies ready:

**Backend (Pytest):**
```bash
docker compose exec backend python -m pytest app/tests/ -v
```

**Frontend (Vitest):**
```bash
# Run locally (production container uses nginx, no npm)
cd frontend && npm test -- --run
```

### Test Coverage

| Area | Framework | Tests | Coverage |
|------|-----------|-------|----------|
| **Backend** | Pytest | 69 | Keywords, Articles, Auth, News Service |
| **Frontend** | Vitest | 23 | App routing, Auth context, KeywordManager |
| **Total** | | **92** | |

**Backend tests include:**
- Keyword creation, retrieval, deletion
- Input validation (empty keywords, duplicates, length limits)
- User isolation (keywords are per-user)
- Article fetching with pagination and sorting
- Match mode (OR/AND keyword logic)
- Username validation (lowercase, alphanumeric only)
- Password and email validation
- JWT token validation
- Authentication endpoints (login, signup, logout)
- News API service mocking (responses, errors, timeouts)

**Frontend tests include:**
- Authentication flow and redirects
- Token persistence in localStorage
- KeywordManager rendering and interactions
- Add/delete keyword operations with loading states
- Error handling and display

## Project Structure

```
newsfeed/
├── docker-compose.yml          # Service orchestration
├── .env.example               # Environment template
├── README.md
│
├── authentik/
│   └── blueprints/            # Auto-configures OAuth2 on startup
│       └── newsfeed-setup.yaml
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── init.sql               # Database initialization
│   └── app/
│       ├── main.py            # FastAPI entry point
│       ├── config.py          # Environment settings
│       ├── database.py        # PostgreSQL connection
│       ├── logging_config.py  # Structured logging setup
│       ├── models/            # SQLAlchemy models
│       ├── schemas/           # Pydantic schemas
│       ├── routers/           # API endpoints (thin controllers)
│       ├── services/          # Business logic & external APIs
│       │   ├── auth_service.py       # Token validation
│       │   ├── authentik_service.py  # Authentik login/signup
│       │   ├── news_service.py       # News API client
│       │   └── openai_service.py     # OpenAI summarization
│       └── tests/             # Pytest tests
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── App.tsx
        ├── context/           # Auth context
        ├── pages/             # Page components
        ├── components/        # Reusable components
        ├── services/          # API client
        └── test/              # Vitest tests
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEWS_API_KEY` | News API key for fetching articles | **Required** |
| `OPENAI_API_KEY` | OpenAI API key for AI summarization (bonus feature) | *Optional* |
| `ENVIRONMENT` | `development` or `production` | `development` |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `INFO` |
| `POSTGRES_USER` | PostgreSQL username | `newsfeed` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `newsfeed_secret` |
| `POSTGRES_DB` | PostgreSQL database name | `newsfeed` |
| `AUTHENTIK_SECRET_KEY` | Authentik secret key | Auto-generated |
| `AUTHENTIK_CLIENT_ID` | OAuth client ID | `newsfeed-app` |

> **Note**: The AI Summary feature requires an OpenAI API key. Get one at https://platform.openai.com/api-keys

## News API Limitations

- **Free Tier**: 100 requests/day
- **Historical Data**: Last 30 days only on free tier
- **Results**: Maximum 100 articles per request

## Why HTTP (Not HTTPS)

This project uses HTTP for local development. This is intentional:

| HTTPS Requirement | Added Complexity |
|-------------------|------------------|
| SSL Certificates | Requires mkcert/openssl installation |
| Self-signed certs | Browser warnings, manual trust required |
| Let's Encrypt | Requires a real domain name |
| Config changes | All URLs need updating (CORS, OAuth, etc.) |

**HTTP is standard for:**
- ✅ Local development environments
- ✅ Portfolio/demo projects
- ✅ Simple `docker compose up` workflow
- ✅ No additional tools required

**For production deployment**, you would add:
- A reverse proxy (Traefik/Caddy) with automatic Let's Encrypt
- A real domain name
- Updated OAuth redirect URIs

## Assumptions & Limitations

1. **Authentication**: Requires Authentik to be running; users can self-register via the signup page
2. **News API**: Free tier has rate limits (100 req/day); articles older than 30 days not available
3. **Keyword Matching**: Uses News API's built-in search, which may not be exact matches
4. **Article Storage**: Articles are not stored locally; each refresh fetches from News API
5. **Single User Session**: Designed for single browser session per user
6. **Username Format**: Only lowercase letters and numbers allowed (no special characters)






