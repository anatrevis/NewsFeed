from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://newsfeed:newsfeed_secret@localhost:5432/newsfeed"
    
    # News API
    news_api_key: str = ""
    news_api_base_url: str = "https://newsapi.org/v2"
    
    # Authentik
    authentik_url: str = "http://localhost:9000"
    authentik_client_id: str = "newsfeed-app"
    
    # CORS
    cors_origins: str = "http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

