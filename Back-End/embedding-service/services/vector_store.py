import httpx
from typing import List, Dict
from config import settings


class VectorStoreService:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.VECTOR_DB_SERVICE_URL,
            timeout=30.0
        )
    
    async def store_embedding(
        self,
        item_id: str,
        field: str,
        embedding: List[float],
        content: str,
        metadata: Dict
    ):
        """Store embedding in vector database"""
        try:
            response = await self.client.post(
                f"/api/v1/index/{field}/upsert",
                json={
                    "id": item_id,
                    "vector": embedding,
                    "payload": {
                        "content": content,
                        "metadata": metadata
                    }
                }
            )
            response.raise_for_status()
            print(f"Stored embedding for {item_id} in field {field}")
        
        except Exception as e:
            raise Exception(f"Failed to store embedding: {e}")
    
    async def close(self):
        """Close connection"""
        await self.client.aclose()
