from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import Optional, List
import uuid

from config import settings
from database import engine, get_db, Base
from models.archive import ArchiveItem
from services.file_service import FileService
from services.instagram_service import InstagramService
from services.message_queue import MessageQueueService
from services.location_service import LocationService
from schemas import (
    TextArchiveRequest,
    InstagramArchiveRequest,
    ArchiveResponse,
    ArchiveListResponse,
    LocationData,
    MapResponse,
    MapMarker
)

# Initialize services
file_service = FileService()
instagram_service = InstagramService()
location_service = LocationService()
mq_service: Optional[MessageQueueService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    global mq_service
    mq_service = MessageQueueService()
    await mq_service.connect()
    
    yield
    
    # Shutdown
    if mq_service:
        await mq_service.close()
    await location_service.close()
    await engine.dispose()


app = FastAPI(
    title="OmniA Archive Service",
    description="Content ingestion service for OmniA",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files for map viewer
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return {
        "service": "OmniA Archive Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/v1/archive/text", response_model=ArchiveResponse, status_code=status.HTTP_201_CREATED)
async def create_text_archive(
    request: TextArchiveRequest,
    db = None  # Will be injected via Depends(get_db)
):
    """
    Archive text content
    
    - **field**: Category/field for the content (e.g., "personal", "work", "inspiration")
    - **title**: Title of the content
    - **content**: The text content to archive
    - **tags**: Optional tags for better organization
    """
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async for session in get_db():
        db = session
        break
    
    # Extract location from content if not provided
    location_data = request.location
    if not location_data:
        extracted_location = await location_service.extract_location_from_text(request.content)
        if extracted_location:
            location_data = LocationData(**extracted_location)
    
    # Create archive item
    item_id = str(uuid.uuid4())
    archive_item = ArchiveItem(
        id=item_id,
        field=request.field,
        content_type="text",
        title=request.title,
        content=request.content,
        tags=request.tags or [],
        location_address=location_data.address if location_data else None,
        location_google_maps_url=location_data.google_maps_url if location_data else None,
        location_latitude=location_data.latitude if location_data else None,
        location_longitude=location_data.longitude if location_data else None
    )
    
    db.add(archive_item)
    await db.commit()
    await db.refresh(archive_item)
    
    # Publish to embedding queue
    await mq_service.publish_to_embedding_queue({
        "item_id": item_id,
        "field": request.field,
        "content_type": "text",
        "content": request.content,
        "metadata": {
            "title": request.title,
            "tags": request.tags or []
        }
    })
    
    # Prepare location data for response
    location_response = None
    if archive_item.location_latitude and archive_item.location_longitude:
        location_response = LocationData(
            address=archive_item.location_address,
            google_maps_url=archive_item.location_google_maps_url,
            latitude=archive_item.location_latitude,
            longitude=archive_item.location_longitude
        )
    
    return ArchiveResponse(
        id=archive_item.id,
        field=archive_item.field,
        content_type=archive_item.content_type,
        title=archive_item.title,
        created_at=archive_item.created_at,
        location=location_response,
        message="Text archived successfully"
    )


@app.post("/api/v1/archive/file", response_model=ArchiveResponse, status_code=status.HTTP_201_CREATED)
async def create_file_archive(
    field: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    tags: Optional[str] = Form(None),
    location_address: Optional[str] = Form(None),
    location_google_maps_url: Optional[str] = Form(None),
    location_latitude: Optional[float] = Form(None),
    location_longitude: Optional[float] = Form(None)
):
    """
    Archive file content
    
    - **field**: Category/field for the content
    - **title**: Title of the content
    - **file**: File to upload
    - **tags**: Optional comma-separated tags
    - **location_address**: Optional address
    - **location_google_maps_url**: Optional Google Maps URL
    - **location_latitude**: Optional latitude
    - **location_longitude**: Optional longitude
    """
    async for session in get_db():
        db = session
        break
    
    # Validate file
    if not file_service.validate_file(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type or size"
        )
    
    # Upload file to MinIO
    file_url = await file_service.upload_file(file, field)
    
    # Extract text content from file
    extracted_content = await file_service.extract_text(file)
    
    # Create archive item
    item_id = str(uuid.uuid4())
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    
    archive_item = ArchiveItem(
        id=item_id,
        field=field,
        content_type="file",
        title=title,
        file_url=file_url,
        file_name=file.filename,
        content=extracted_content,
        tags=tag_list,
        location_address=location_address,
        location_google_maps_url=location_google_maps_url,
        location_latitude=location_latitude,
        location_longitude=location_longitude
    )
    
    db.add(archive_item)
    await db.commit()
    await db.refresh(archive_item)
    
    # Publish to embedding queue
    await mq_service.publish_to_embedding_queue({
        "item_id": item_id,
        "field": field,
        "content_type": "file",
        "content": extracted_content,
        "file_url": file_url,
        "metadata": {
            "title": title,
            "file_name": file.filename,
            "tags": tag_list
        }
    })
    
    # Prepare location data for response
    location_response = None
    if location_latitude and location_longitude:
        location_response = LocationData(
            address=location_address,
            google_maps_url=location_google_maps_url,
            latitude=location_latitude,
            longitude=location_longitude
        )
    
    return ArchiveResponse(
        id=archive_item.id,
        field=archive_item.field,
        content_type=archive_item.content_type,
        title=archive_item.title,
        created_at=archive_item.created_at,
        file_url=file_url,
        location=location_response,
        message="File archived successfully"
    )


@app.post("/api/v1/archive/instagram", response_model=ArchiveResponse, status_code=status.HTTP_201_CREATED)
async def create_instagram_archive(request: InstagramArchiveRequest):
    """
    Archive Instagram content
    
    - **field**: Category/field for the content
    - **title**: Title of the content
    - **instagram_url**: Instagram post/reel URL
    - **tags**: Optional tags
    - **location**: Optional location data
    """
    async for session in get_db():
        db = session
        break
    
    # Fetch Instagram content
    instagram_data = await instagram_service.fetch_content(request.instagram_url)
    
    # Use provided location or extract from caption
    location_data = request.location
    if not location_data and instagram_data["caption"]:
        extracted_location = await location_service.extract_location_from_text(instagram_data["caption"])
        if extracted_location:
            location_data = LocationData(**extracted_location)
    
    # Create archive item
    item_id = str(uuid.uuid4())
    archive_item = ArchiveItem(
        id=item_id,
        field=request.field,
        content_type="instagram",
        title=request.title,
        content=instagram_data["caption"],
        file_url=instagram_data.get("media_url"),
        extra_metadata=instagram_data["metadata"],
        tags=request.tags or [],
        location_address=location_data.address if location_data else None,
        location_google_maps_url=location_data.google_maps_url if location_data else None,
        location_latitude=location_data.latitude if location_data else None,
        location_longitude=location_data.longitude if location_data else None
    )
    
    db.add(archive_item)
    await db.commit()
    await db.refresh(archive_item)
    
    # Publish to embedding queue
    await mq_service.publish_to_embedding_queue({
        "item_id": item_id,
        "field": request.field,
        "content_type": "instagram",
        "content": instagram_data["caption"],
        "media_url": instagram_data.get("media_url"),
        "metadata": {
            "title": request.title,
            "instagram_url": str(request.instagram_url),
            "tags": request.tags or [],
            **instagram_data["metadata"]
        }
    })
    
    # Prepare location data for response
    location_response = None
    if archive_item.location_latitude and archive_item.location_longitude:
        location_response = LocationData(
            address=archive_item.location_address,
            google_maps_url=archive_item.location_google_maps_url,
            latitude=archive_item.location_latitude,
            longitude=archive_item.location_longitude
        )
    
    return ArchiveResponse(
        id=archive_item.id,
        field=archive_item.field,
        content_type=archive_item.content_type,
        title=archive_item.title,
        created_at=archive_item.created_at,
        location=location_response,
        message="Instagram content archived successfully"
    )


@app.get("/api/v1/archive/items", response_model=ArchiveListResponse)
async def list_all_archive_items(
    field: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """List archive items, optionally filtered by field"""
    from sqlalchemy import select
    
    async for session in get_db():
        db = session
        break
    
    # Build query with optional field filter
    if field:
        query = select(ArchiveItem).where(ArchiveItem.field == field).offset(skip).limit(limit)
        count_query = select(ArchiveItem).where(ArchiveItem.field == field)
    else:
        query = select(ArchiveItem).offset(skip).limit(limit)
        count_query = select(ArchiveItem)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Count total items
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    # Build response items with location data
    response_items = []
    for item in items:
        location_response = None
        if item.location_latitude and item.location_longitude:
            location_response = LocationData(
                address=item.location_address,
                google_maps_url=item.location_google_maps_url,
                latitude=item.location_latitude,
                longitude=item.location_longitude
            )
        
        response_items.append(
            ArchiveResponse(
                id=item.id,
                field=item.field,
                content_type=item.content_type,
                title=item.title,
                created_at=item.created_at,
                file_url=item.file_url,
                location=location_response
            )
        )
    
    return ArchiveListResponse(
        items=response_items,
        total=total,
        skip=skip,
        limit=limit
    )


@app.get("/api/v1/archive/{field}", response_model=ArchiveListResponse)
async def list_archive_items_by_field(
    field: str,
    skip: int = 0,
    limit: int = 50
):
    """List archive items for a specific field (legacy endpoint)"""
    from sqlalchemy import select
    
    async for session in get_db():
        db = session
        break
    
    query = select(ArchiveItem).where(ArchiveItem.field == field).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Count total items
    count_query = select(ArchiveItem).where(ArchiveItem.field == field)
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    # Build response items with location data
    response_items = []
    for item in items:
        location_response = None
        if item.location_latitude and item.location_longitude:
            location_response = LocationData(
                address=item.location_address,
                google_maps_url=item.location_google_maps_url,
                latitude=item.location_latitude,
                longitude=item.location_longitude
            )
        
        response_items.append(
            ArchiveResponse(
                id=item.id,
                field=item.field,
                content_type=item.content_type,
                title=item.title,
                created_at=item.created_at,
                file_url=item.file_url,
                location=location_response
            )
        )
    
    return ArchiveListResponse(
        items=response_items,
        total=total,
        skip=skip,
        limit=limit
    )


@app.delete("/api/v1/archive/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_archive_item(item_id: str):
    """Delete an archive item"""
    from sqlalchemy import select
    
    async for session in get_db():
        db = session
        break
    
    query = select(ArchiveItem).where(ArchiveItem.id == item_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archive item not found"
        )
    
    # Delete file from MinIO if exists
    if item.file_url:
        await file_service.delete_file(item.file_url)
    
    await db.delete(item)
    await db.commit()
    
    return None


@app.get("/api/v1/archive/map/all", response_model=MapResponse)
async def get_map_view(
    field: Optional[str] = None,
    tags: Optional[str] = None
):
    """
    Get map view with all items that have location data
    
    - **field**: Optional filter by field
    - **tags**: Optional comma-separated tags to filter
    """
    from sqlalchemy import select, and_
    
    async for session in get_db():
        db = session
        break
    
    # Build query for items with location
    conditions = [
        ArchiveItem.location_latitude.isnot(None),
        ArchiveItem.location_longitude.isnot(None)
    ]
    
    if field:
        conditions.append(ArchiveItem.field == field)
    
    query = select(ArchiveItem).where(and_(*conditions))
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Filter by tags if provided
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        items = [item for item in items if any(tag in (item.tags or []) for tag in tag_list)]
    
    # Create markers
    markers = []
    total_lat = 0
    total_lon = 0
    
    for item in items:
        markers.append(MapMarker(
            id=item.id,
            title=item.title,
            latitude=item.location_latitude,
            longitude=item.location_longitude,
            field=item.field,
            content_preview=item.content[:100] if item.content else None,
            created_at=item.created_at
        ))
        total_lat += item.location_latitude
        total_lon += item.location_longitude
    
    # Calculate center point
    center_lat = total_lat / len(markers) if markers else None
    center_lon = total_lon / len(markers) if markers else None
    
    return MapResponse(
        markers=markers,
        total=len(markers),
        center_latitude=center_lat,
        center_longitude=center_lon
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
