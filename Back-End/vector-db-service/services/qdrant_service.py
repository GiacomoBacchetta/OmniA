from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Optional
from config import settings


class QdrantService:
    def __init__(self):
        self.client: Optional[AsyncQdrantClient] = None
    
    async def initialize(self):
        """Initialize Qdrant client"""
        self.client = AsyncQdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
            timeout=30.0
        )
        print(f"Connected to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
    
    async def health_check(self) -> bool:
        """Check if Qdrant is healthy"""
        try:
            # Try to list collections as a health check
            await self.client.get_collections()
            return True
        except Exception as e:
            print(f"Qdrant health check failed: {e}")
            return False
    
    def _get_distance_metric(self):
        """Get distance metric enum"""
        metric_map = {
            "Cosine": Distance.COSINE,
            "Euclidean": Distance.EUCLID,
            "Dot": Distance.DOT
        }
        return metric_map.get(settings.DISTANCE_METRIC, Distance.COSINE)
    
    async def create_collection(self, collection_name: str, vector_size: int):
        """Create a new collection"""
        try:
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=self._get_distance_metric()
                )
            )
            print(f"Created collection: {collection_name}")
        except Exception as e:
            # Collection might already exist
            print(f"Collection creation error (might already exist): {e}")
            raise
    
    async def delete_collection(self, collection_name: str):
        """Delete a collection"""
        await self.client.delete_collection(collection_name=collection_name)
        print(f"Deleted collection: {collection_name}")
    
    async def get_collection_stats(self, collection_name: str):
        """Get collection statistics"""
        info = await self.client.get_collection(collection_name=collection_name)
        return {
            "name": collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status,
            "config": {
                "vector_size": info.config.params.vectors.size,
                "distance": str(info.config.params.vectors.distance)
            }
        }
    
    async def list_collections(self) -> List[str]:
        """List all collections"""
        collections = await self.client.get_collections()
        return [col.name for col in collections.collections]
    
    async def upsert_point(
        self,
        collection_name: str,
        point_id: str,
        vector: List[float],
        payload: dict
    ):
        """Insert or update a point in the collection"""
        # Ensure collection exists
        try:
            await self.client.get_collection(collection_name=collection_name)
        except Exception:
            # Create collection if it doesn't exist
            await self.create_collection(collection_name, len(vector))
        
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload=payload
        )
        
        await self.client.upsert(
            collection_name=collection_name,
            points=[point]
        )
    
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None
    ):
        """Search for similar vectors"""
        results = await self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold
        )
        return results
    
    async def get_point(self, collection_name: str, point_id: str):
        """Get a specific point"""
        points = await self.client.retrieve(
            collection_name=collection_name,
            ids=[point_id]
        )
        if not points:
            raise Exception(f"Point {point_id} not found")
        return points[0]
    
    async def delete_point(self, collection_name: str, point_id: str):
        """Delete a specific point"""
        await self.client.delete(
            collection_name=collection_name,
            points_selector=[point_id]
        )
