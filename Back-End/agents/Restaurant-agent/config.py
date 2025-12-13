from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Service Configuration
    SERVICE_NAME: str = "field-agent-template"
    PORT: int = 8010
    FIELD_NAME: str = "example_field"
    
    # Vector DB Configuration
    VECTOR_DB_SERVICE_URL: str
    
    # Ollama Configuration
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama2"
    
    # Orchestrator Configuration
    ORCHESTRATOR_URL: str
    AUTO_REGISTER: bool = True
    
    # HuggingFace Configuration
    HF_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    HF_CACHE_DIR: str = "/app/models_cache"
    
    # RAG Configuration
    MAX_CONTEXT_LENGTH: int = 2000
    TOP_K_RESULTS: int = 5
    SCORE_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
