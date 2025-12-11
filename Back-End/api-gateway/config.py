from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Service Configuration
    SERVICE_NAME: str = "api-gateway"
    PORT: int = 8000
    
    # JWT Configuration
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    
    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Service URLs
    ARCHIVE_SERVICE_URL: str = "https://localhost:8001"
    EMBEDDING_SERVICE_URL: str = "https://localhost:8002"
    VECTOR_DB_SERVICE_URL: str = "https://localhost:8003"
    ORCHESTRATOR_SERVICE_URL: str = "https://localhost:8004"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
