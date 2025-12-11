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
    HF_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    HF_CACHE_DIR: str = "/app/models_cache"
    
    # Vector DB Configuration
    VECTOR_DB_SERVICE_URL: str
    
    # Processing Configuration
    BATCH_SIZE: int = 10
    MAX_WORKERS: int = 2
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
