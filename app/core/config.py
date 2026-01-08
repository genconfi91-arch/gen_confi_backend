"""
Application configuration management.
Loads environment variables and provides typed configuration.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    # Application
    APP_NAME: str = Field(default="FastAPI PostgreSQL API", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # Database
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL database connection URL",
        examples=["postgresql://user:password@localhost:5432/dbname"]
    )
    
    # API
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 prefix")
    
    # Security
    SECRET_KEY: str = Field(
        ...,
        description="Secret key for JWT and encryption",
        min_length=32
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Token expiration in minutes")
    
    # CORS (as string, will be parsed)
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000,http://10.0.2.2:8000",
        description="Allowed CORS origins (comma-separated)"
    )
    
    # Admin Credentials (Hardcoded)
    ADMIN_EMAIL: str = Field(default="admin@genconfi.com", description="Admin email")
    ADMIN_PASSWORD: str = Field(default="admin123", description="Admin password")
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


# Global settings instance
settings = Settings()

