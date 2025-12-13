from fastapi import FastAPI, HTTPException, status
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging

from config import settings
from services.qdrant_service import QdrantService

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Qdrant service
qdrant_service = QdrantService()

app = FastAPI(
    title="OmniA Vector DB Service",
    description="Vector database wrapper for Qdrant",
    version="1.0.0"
)


class UpsertRequest(BaseModel):
    id: str
    vector: List[float]
    payload: Dict


class SearchRequest(BaseModel):
    vector: List[float]
    limit: int = 10
    score_threshold: Optional[float] = None


class SearchResult(BaseModel):
    id: str
    score: float
    payload: Dict


@app.on_event("startup")
async def startup():
    """Initialize Qdrant client"""
    await qdrant_service.initialize()


@app.get("/")
async def root():
    return {
        "service": "OmniA Vector DB Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    is_healthy = await qdrant_service.health_check()
    if is_healthy:
        return {"status": "healthy"}
    raise HTTPException(status_code=503, detail="Qdrant is not healthy")


@app.post("/api/v1/index/{field}", status_code=status.HTTP_201_CREATED)
async def create_index(field: str, vector_size: Optional[int] = None):
    """Create a new collection (index) for a field"""
    try:
        size = vector_size or settings.DEFAULT_VECTOR_SIZE
        await qdrant_service.create_collection(field, size)
        return {"message": f"Collection created for field: {field}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/index/{field}/stats")
async def get_index_stats(field: str):
    """Get statistics for a field's collection"""
    try:
        stats = await qdrant_service.get_collection_stats(field)
        return stats
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/api/v1/index/{field}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_index(field: str):
    """Delete a collection"""
    try:
        await qdrant_service.delete_collection(field)
        return None
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/v1/index/{field}/upsert", status_code=status.HTTP_200_OK)
async def upsert_vector(field: str, request: UpsertRequest):
    """Insert or update a vector in the collection"""
    try:
        await qdrant_service.upsert_point(
            collection_name=field,
            point_id=request.id,
            vector=request.vector,
            payload=request.payload
        )
        return {"message": "Vector upserted successfully", "id": request.id}
    except Exception as e:
        print(f"ERROR in upsert_vector: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/index/{field}/search", response_model=List[SearchResult])
async def search_vectors(field: str, request: SearchRequest):
    """Search for similar vectors in the collection"""
    try:
        logger.info(f"Searching collection: {field}, vector length: {len(request.vector)}, limit: {request.limit}")
        results = await qdrant_service.search(
            collection_name=field,
            query_vector=request.vector,
            limit=request.limit,
            score_threshold=request.score_threshold
        )
        
        return [
            SearchResult(
                id=str(result.id),
                score=result.score,
                payload=result.payload
            )
            for result in results
        ]
    except Exception as e:
        logger.error(f"Search failed for collection {field}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/index/{field}/point/{point_id}")
async def get_point(field: str, point_id: str):
    """Get a specific point from the collection"""
    try:
        point = await qdrant_service.get_point(field, point_id)
        return point
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/api/v1/index/{field}/point/{point_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_point(field: str, point_id: str):
    """Delete a specific point from the collection"""
    try:
        await qdrant_service.delete_point(field, point_id)
        return None
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/v1/collections")
async def list_collections():
    """List all collections"""
    try:
        collections = await qdrant_service.list_collections()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
