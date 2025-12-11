from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Service Configuration
    SERVICE_NAME: str = "archive-service"
    PORT: int = 8001
    
    # Database Configuration
    DATABASE_URL: str
    
    # RabbitMQ Configuration
    RABBITMQ_URL: str
    EMBEDDING_QUEUE_NAME: str = "embedding_queue"
    
    # MinIO Configuration
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str = "omnia-archive"
    MINIO_SECURE: bool = False
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_FILE_TYPES: List[str] = [
        "pdf", "docx", "txt", "md",
        "png", "jpg", "jpeg", "gif",
        "mp4", "mp3"
    ]
    
    # Instagram Configuration
    INSTAGRAM_SESSION_FILE: str = "/app/data/instagram_session"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
