from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Service Configuration
    SERVICE_NAME: str = "vector-db-service"
    PORT: int = 8003
    
    # Qdrant Configuration
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""
    
    # Collection Configuration
    DEFAULT_VECTOR_SIZE: int = 384  # For sentence-transformers/all-MiniLM-L6-v2
    DISTANCE_METRIC: str = "Cosine"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
