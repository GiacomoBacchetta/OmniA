from sqlalchemy import Column, String, Text, DateTime, JSON, ARRAY, Float
from sqlalchemy.sql import func
from database import Base
import uuid


class ArchiveItem(Base):
    __tablename__ = "archive_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    field = Column(String, nullable=False, index=True)  # Category/field name
    content_type = Column(String, nullable=False)  # text, file, instagram
    title = Column(String, nullable=False)
    content = Column(Text)  # Extracted or raw text content
    file_url = Column(String)  # MinIO file URL
    file_name = Column(String)  # Original filename
    extra_metadata = Column(JSON)  # Additional metadata
    tags = Column(ARRAY(String))  # Tags for organization
    
    # Location fields
    location_address = Column(String)  # Street address or place name
    location_google_maps_url = Column(String)  # Google Maps link
    location_latitude = Column(Float)  # Latitude coordinate
    location_longitude = Column(Float)  # Longitude coordinate
    location_metadata = Column(JSON)  # Additional location info (place_id, etc.)
    
    # Embedding status and vector
    embedding_status = Column(String, default="pending")  # pending, processing, completed, failed
    embedding_created_at = Column(DateTime(timezone=True))  # When embedding was created
    embedding_vector = Column(JSON)  # The embedding vector stored as JSON array
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ArchiveItem {self.id} - {self.field} - {self.title}>"
