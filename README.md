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

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Authentication | Authentik (OAuth2/OIDC) |
| Database | PostgreSQL 15 |
| External API | [News API](https://newsapi.org) |
| Infrastructure | Docker Compose |
| Testing | Pytest, Vitest |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Docker Compose Network                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │    Frontend      │              │    Authentik     │         │
│  │  React + TS      │◄────────────►│   OAuth2/OIDC    │         │
│  │  :3000           │              │   :9000          │         │
│  └────────┬─────────┘              └──────────────────┘         │
│           │                                 ▲                    │
│           ▼                                 │                    │
│  ┌──────────────────────────────────────────┴───────────┐       │
│  │                   FastAPI Backend                     │       │
│  │                       :8000                           │       │
│  └───────────────┬─────────────────────┬────────────────┘       │
│                  │                     │                         │
│                  ▼                     ▼                         │
│  ┌──────────────────────┐     ┌──────────────────────┐          │
│  │      PostgreSQL      │     │      News API        │          │
│  │      :5432           │     │   (External)         │          │
│  │  • newsfeed db       │     │                      │          │
│  │  • authentik db      │     │                      │          │
│  └──────────────────────┘     └──────────────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- News API key (get one free at https://newsapi.org/register)

### Setup (3 steps!)

1. **Clone and configure**
   ```bash
   git clone https://github.com/anatrevis/NewsFeed.git
   cd NewsFeed
   cp .env.example .env
   ```

2. **Add your News API key** - Edit `.env` and replace:
   ```
   NEWS_API_KEY=your-actual-newsapi-key-here
   ```
   > All other values are pre-configured and ready to use!

3. **Start everything**
   ```bash
   docker-compose up -d
   ```

That's it! Wait ~2-3 minutes for first-time initialization, then access:
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
docker compose exec frontend npm test -- --run
```

### Running Locally

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-mock
pytest app/tests/ -v
```

**Frontend:**
```bash
cd frontend
npm install
npm test        # Watch mode
npm test -- --run  # Single run
```

### Test Coverage

| Area | Framework | Tests | Coverage |
|------|-----------|-------|----------|
| **Backend** | Pytest | 69 | Keywords, Articles, Auth, News Service |
| **Frontend** | Vitest | 19 | App routing, Auth context, KeywordManager |

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
│       ├── schemas/           # Pydantic models
│       ├── routers/           # API endpoints
│       ├── services/          # Business logic
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
| `ENVIRONMENT` | `development` or `production` | `development` |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `INFO` |
| `POSTGRES_USER` | PostgreSQL username | `newsfeed` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `newsfeed_secret` |
| `POSTGRES_DB` | PostgreSQL database name | `newsfeed` |
| `AUTHENTIK_SECRET_KEY` | Authentik secret key | Auto-generated |
| `AUTHENTIK_CLIENT_ID` | OAuth client ID | `newsfeed-app` |

## News API Limitations

- **Free Tier**: 100 requests/day
- **Historical Data**: Last 30 days only on free tier
- **Results**: Maximum 100 articles per request

## Assumptions & Limitations

1. **Authentication**: Requires Authentik to be running; users can self-register via the signup page
2. **News API**: Free tier has rate limits (100 req/day); articles older than 30 days not available
3. **Keyword Matching**: Uses News API's built-in search, which may not be exact matches
4. **Article Storage**: Articles are not stored locally; each refresh fetches from News API
5. **Single User Session**: Designed for single browser session per user
6. **Username Format**: Only lowercase letters and numbers allowed (no special characters)

## Development

### Running locally without Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Note: You'll still need PostgreSQL and Authentik running for full functionality.

## License

MIT

