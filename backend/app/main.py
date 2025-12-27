from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import keywords, articles

settings = get_settings()

app = FastAPI(
    title="NewsFeed API",
    description="Personalized News Feed Application API",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(keywords.router, prefix="/api/keywords", tags=["Keywords"])
app.include_router(articles.router, prefix="/api/articles", tags=["Articles"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "newsfeed-api"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to NewsFeed API",
        "docs": "/docs",
        "health": "/health",
    }

