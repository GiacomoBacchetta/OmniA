from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


class LocationData(BaseModel):
    """Location information"""
    address: Optional[str] = None
    google_maps_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class TextArchiveRequest(BaseModel):
    field: str
    title: str
    content: str
    tags: Optional[List[str]] = None
    location: Optional[LocationData] = None


class InstagramArchiveRequest(BaseModel):
    field: str
    title: str
    instagram_url: HttpUrl
    tags: Optional[List[str]] = None
    location: Optional[LocationData] = None


class UpdateArchiveRequest(BaseModel):
    """Request to update an archive item"""
    field: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[LocationData] = None


class EmbeddingStatusUpdate(BaseModel):
    """Request to update embedding status"""
    embedding_status: str  # pending, processing, completed, failed
    embedding_created_at: Optional[str] = None
    embedding_vector: Optional[List[float]] = None  # The embedding vector


class ArchiveResponse(BaseModel):
    id: str
    field: str
    content_type: str
    title: str
    created_at: datetime
    file_url: Optional[str] = None
    message: Optional[str] = None
    location: Optional[LocationData] = None
    embedding_status: Optional[str] = "pending"
    embedding_created_at: Optional[datetime] = None
    embedding_vector: Optional[List[float]] = None  # Include only when needed
    
    class Config:
        from_attributes = True


class ArchiveListResponse(BaseModel):
    items: List[ArchiveResponse]
    total: int
    skip: int
    limit: int


class MapMarker(BaseModel):
    """Marker for map visualization"""
    id: str
    title: str
    latitude: float
    longitude: float
    field: str
    content_preview: Optional[str] = None
    created_at: datetime


class MapResponse(BaseModel):
    """Map with all location markers"""
    markers: List[MapMarker]
    total: int
    center_latitude: Optional[float] = None
    center_longitude: Optional[float] = None
