from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Service Configuration
    SERVICE_NAME: str = "orchestrator-service"
    PORT: int = 8004
    
    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1
    
    # Ollama Configuration
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "phi"
    
    # Vector DB Configuration
    VECTOR_DB_SERVICE_URL: str
    
    # Agent Configuration
    DEFAULT_AGENT_PORT_RANGE_START: int = 8010
    MAX_AGENTS: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
