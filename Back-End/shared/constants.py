"""
Shared constants across services
"""

# Service Ports
API_GATEWAY_PORT = 8000
ARCHIVE_SERVICE_PORT = 8001
EMBEDDING_SERVICE_PORT = 8002
VECTOR_DB_SERVICE_PORT = 8003
ORCHESTRATOR_SERVICE_PORT = 8004
AGENT_PORT_START = 8010

# Queue Names
EMBEDDING_QUEUE = "embedding_queue"

# Default Field Names
DEFAULT_FIELDS = [
    "personal",
    "work",
    "inspiration",
    "learning",
    "health",
    "finance"
]

# File Types
ALLOWED_TEXT_FORMATS = ["txt", "md", "json", "csv"]
ALLOWED_DOC_FORMATS = ["pdf", "docx", "doc", "pptx", "xlsx"]
ALLOWED_IMAGE_FORMATS = ["png", "jpg", "jpeg", "gif", "svg"]
ALLOWED_VIDEO_FORMATS = ["mp4", "mov", "avi"]
ALLOWED_AUDIO_FORMATS = ["mp3", "wav", "m4a"]

ALL_ALLOWED_FORMATS = (
    ALLOWED_TEXT_FORMATS +
    ALLOWED_DOC_FORMATS +
    ALLOWED_IMAGE_FORMATS +
    ALLOWED_VIDEO_FORMATS +
    ALLOWED_AUDIO_FORMATS
)

# Embedding Models
DEFAULT_HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_OLLAMA_MODEL = "llama2"

# Vector DB
DEFAULT_VECTOR_SIZE = 384  # For all-MiniLM-L6-v2
DEFAULT_TOP_K = 5
DEFAULT_SCORE_THRESHOLD = 0.7

# RAG
MAX_CONTEXT_LENGTH = 2000
MAX_QUERY_LENGTH = 500
