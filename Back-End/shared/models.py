"""
Common Pydantic models used across services
"""
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    TEXT = "text"
    FILE = "file"
    INSTAGRAM = "instagram"


class FieldType(str, Enum):
    PERSONAL = "personal"
    WORK = "work"
    INSPIRATION = "inspiration"
    LEARNING = "learning"
    HEALTH = "health"
    FINANCE = "finance"
    CUSTOM = "custom"


class BaseArchiveItem(BaseModel):
    """Base model for archive items"""
    id: str
    field: str
    content_type: ContentType
    title: str
    content: Optional[str] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None


class VectorSearchResult(BaseModel):
    """Result from vector search"""
    id: str
    score: float
    content: str
    metadata: Dict


class EmbeddingMessage(BaseModel):
    """Message format for embedding queue"""
    item_id: str
    field: str
    content_type: str
    content: str
    metadata: Dict = {}
