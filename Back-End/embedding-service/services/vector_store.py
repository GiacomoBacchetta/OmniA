import httpx
from typing import List, Dict
from datetime import datetime
from config import settings


class VectorStoreService:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.VECTOR_DB_SERVICE_URL,
            timeout=30.0
        )
        self.archive_client = httpx.AsyncClient(
            base_url=settings.ARCHIVE_SERVICE_URL,
            timeout=10.0
        )
    
    async def store_embedding(
        self,
        item_id: str,
        field: str,
        embedding: List[float],
        content: str,
        metadata: Dict
    ):
        """Store embedding in vector database and update archive status"""
        try:
            # Store in vector DB
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
            
            # Update archive item status with embedding vector
            await self._update_archive_embedding_status(
                item_id=item_id,
                status="completed",
                embedding_vector=embedding
            )
        
        except Exception as e:
            # Mark as failed in archive
            await self._update_archive_embedding_status(
                item_id=item_id,
                status="failed"
            )
            raise Exception(f"Failed to store embedding: {e}")
    
    async def _update_archive_embedding_status(
        self,
        item_id: str,
        status: str,
        embedding_vector: List[float] = None
    ):
        """Update the embedding status and vector in the archive service"""
        try:
            payload = {
                "embedding_status": status,
                "embedding_created_at": datetime.utcnow().isoformat()
            }
            if embedding_vector:
                payload["embedding_vector"] = embedding_vector
            
            response = await self.archive_client.patch(
                f"/api/v1/archive/{item_id}/embedding-status",
                json=payload
            )
            response.raise_for_status()
            print(f"Updated embedding status for {item_id}: {status}")
        except Exception as e:
            print(f"Warning: Failed to update archive embedding status: {e}")
    
    async def close(self):
        """Close connections"""
        await self.client.aclose()
        await self.archive_client.aclose()
