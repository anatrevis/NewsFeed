# NewsFeed - Personalized News Application

A full-stack news aggregator where authenticated users save keyword preferences and view personalized articles from [News API](https://newsapi.org).

## Features

- **User Authentication**: OAuth2/OIDC via Authentik with PKCE flow
- **Keyword Management**: Save and delete personal keyword preferences
- **Personalized Feed**: View articles filtered by your keywords
- **Article Details**: Click into articles for more detail with links to full articles
- **Responsive UI**: Modern React interface with Tailwind CSS

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

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd newsfeed
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Add your News API key to `.env`**
   ```
   NEWS_API_KEY=your-newsapi-key-here
   ```

4. **Start all services**
   ```bash
   docker-compose up -d
   ```

5. **Wait for services to initialize** (first run takes ~2-3 minutes)
   ```bash
   docker-compose logs -f
   ```

6. **Access the applications**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - Authentik Admin: http://localhost:9000

### Authentik Setup (Required)

After first login to Authentik at http://localhost:9000:

**Default Admin Credentials**: `akadmin` / `admin123`

1. **Create Application**
   - Go to: Admin → Applications → Create
   - Name: `NewsFeed`
   - Slug: `newsfeed-app`
   - Launch URL: `http://localhost:3000`

2. **Create OAuth Provider**
   - Go to: Admin → Providers → Create → OAuth2/OpenID Provider
   - Name: `NewsFeed Provider`
   - Client ID: `newsfeed-app`
   - Client type: `Public`
   - Redirect URIs: `http://localhost:3000/callback`
   - Signing Key: Select any available key

3. **Link Provider to Application**
   - Edit the application and select the provider

4. **Create a User** (for testing)
   - Go to: Admin → Directory → Users → Create
   - Fill in username, email, and password
   - This user can now log in to the NewsFeed app

## How Keyword Filtering Works

1. **Add Keywords**: Users add keywords that matter to them (e.g., "python", "AI", "climate")

2. **Keyword Storage**: Keywords are stored in PostgreSQL, associated with the user's ID from Authentik

3. **Article Fetching**: When viewing the feed:
   - Backend retrieves user's keywords
   - Combines them with OR logic (e.g., `python OR AI OR climate`)
   - Sends query to News API's `/everything` endpoint
   - Returns matching articles from the last 30 days

4. **Results**: Users see articles from various sources matching their interests

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/keywords` | Get user's saved keywords | Required |
| POST | `/api/keywords` | Add a keyword | Required |
| DELETE | `/api/keywords/{keyword}` | Remove a keyword | Required |
| GET | `/api/articles` | Get articles for user's keywords | Required |
| GET | `/health` | Health check | Public |

## Running Tests

### Backend Tests
```bash
cd backend
pip install -r requirements.txt
pytest
```

### Frontend Tests
```bash
cd frontend
npm install
npm test
```

## Project Structure

```
newsfeed/
├── docker-compose.yml          # Service orchestration
├── .env.example               # Environment template
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py            # FastAPI entry point
│       ├── config.py          # Environment settings
│       ├── database.py        # PostgreSQL connection
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

| Variable | Description | Required |
|----------|-------------|----------|
| `NEWS_API_KEY` | News API key for fetching articles | Yes |
| `POSTGRES_USER` | PostgreSQL username (default: `newsfeed`) | No |
| `POSTGRES_PASSWORD` | PostgreSQL password | No |
| `POSTGRES_DB` | PostgreSQL database name (default: `newsfeed`) | No |
| `AUTHENTIK_SECRET_KEY` | Authentik secret key | No |
| `AUTHENTIK_CLIENT_ID` | OAuth client ID (default: `newsfeed-app`) | No |

## News API Limitations

- **Free Tier**: 100 requests/day
- **Historical Data**: Last 30 days only on free tier
- **Results**: Maximum 100 articles per request

## Assumptions & Limitations

1. **Authentication**: Requires Authentik setup - users must be created in Authentik admin
2. **News API**: Free tier has rate limits; articles older than 30 days not available
3. **Keyword Matching**: Uses News API's built-in search, which may not be exact matches
4. **Article Storage**: Articles are not stored locally; each refresh fetches from News API
5. **Single User Session**: Designed for single browser session per user

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

