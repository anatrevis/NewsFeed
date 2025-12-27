from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

from app.config import get_settings
from app.logging_config import setup_logging, get_logger
from app.routers import keywords, articles, auth, summarize

settings = get_settings()

# Initialize logging
setup_logging(
    environment=settings.environment,
    log_level=settings.log_level,
)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info(
        f"NewsFeed API starting | "
        f"environment={settings.environment} | "
        f"cors_origins={settings.cors_origins}"
    )
    yield
    # Shutdown
    logger.info("NewsFeed API shutting down")


app = FastAPI(
    title="NewsFeed API",
    description="Personalized News Feed Application API",
    version="1.0.0",
    lifespan=lifespan,
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    
    # Log request (skip health checks in production to reduce noise)
    if settings.environment != "production" or request.url.path != "/health":
        logger.info(
            f"{request.method} {request.url.path} | "
            f"status={response.status_code} | "
            f"duration={duration_ms:.2f}ms"
        )
    
    return response


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(keywords.router, prefix="/api/keywords", tags=["Keywords"])
app.include_router(articles.router, prefix="/api/articles", tags=["Articles"])
app.include_router(summarize.router, prefix="/api/summarize", tags=["Summarize"])


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
