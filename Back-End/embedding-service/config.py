from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Service Configuration
    SERVICE_NAME: str = "embedding-service"
    PORT: int = 8002
    
    # RabbitMQ Configuration
    RABBITMQ_URL: str
    EMBEDDING_QUEUE_NAME: str = "embedding_queue"
    
    # Ollama Configuration
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama2"
    
    # HuggingFace Configuration
    HF_MODEL: str = "google/gemma-2-2b-it"
    HF_CACHE_DIR: str = "/app/models_cache"
    
    # Embedding Strategy: "ollama" or "huggingface"
    EMBEDDING_STRATEGY: str = "huggingface"  # Use HuggingFace with 768 dimensions
    
    # Vector DB Configuration
    VECTOR_DB_SERVICE_URL: str
    
    # Archive Service Configuration (for status callbacks)
    ARCHIVE_SERVICE_URL: str = "http://archive-service:8001"
    
    # Processing Configuration
    BATCH_SIZE: int = 10
    MAX_WORKERS: int = 2
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
