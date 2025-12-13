import httpx
from sentence_transformers import SentenceTransformer
from typing import List
from config import settings
import os


class EmbeddingGenerator:
    def __init__(self):
        # Initialize HuggingFace model
        os.makedirs(settings.HF_CACHE_DIR, exist_ok=True)
        self.hf_model = SentenceTransformer(
            settings.HF_MODEL,
            cache_folder=settings.HF_CACHE_DIR
        )
        
        # Ollama client
        self.ollama_client = httpx.AsyncClient(base_url=settings.OLLAMA_URL, timeout=60.0)
    
    async def generate_embedding(self, text: str, content_type: str = "text") -> List[float]:
        """
        Generate embedding for text
        
        Strategy:
        - Use Ollama for large embeddings if configured
        - Fallback to HuggingFace for fast, consistent embeddings
        """
        try:
            # Check embedding strategy from settings
            if settings.EMBEDDING_STRATEGY == "ollama":
                return await self._generate_ollama_embedding(text)
            else:
                return await self._generate_hf_embedding(text)
        
        except Exception as e:
            print(f"Error generating embedding with {settings.EMBEDDING_STRATEGY}: {e}")
            # Fallback to alternative method
            try:
                if settings.EMBEDDING_STRATEGY == "ollama":
                    print("Falling back to HuggingFace...")
                    return await self._generate_hf_embedding(text)
                else:
                    print("Falling back to Ollama...")
                    return await self._generate_ollama_embedding(text)
            except Exception as fallback_error:
                print(f"Fallback also failed: {fallback_error}")
                raise
    
    async def _generate_hf_embedding(self, text: str) -> List[float]:
        """Generate embedding using HuggingFace model"""
        # Truncate text if too long (model specific limit)
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]
        
        # Generate embedding
        embedding = self.hf_model.encode(text, convert_to_tensor=False)
        embedding_list = embedding.tolist()
        
        # Ensure 768 dimensions (gemma-2-2b-it produces 768d embeddings)
        # If the model produces different dimensions, pad or truncate
        target_dim = 768
        if len(embedding_list) < target_dim:
            # Pad with zeros
            embedding_list.extend([0.0] * (target_dim - len(embedding_list)))
        elif len(embedding_list) > target_dim:
            # Truncate to target dimension
            embedding_list = embedding_list[:target_dim]
        
        return embedding_list
    
    async def _generate_ollama_embedding(self, text: str) -> List[float]:
        """Generate embedding using Ollama"""
        try:
            response = await self.ollama_client.post(
                "/api/embeddings",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": text
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["embedding"]
        
        except Exception as e:
            raise Exception(f"Ollama embedding failed: {e}")
    
    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = self.hf_model.encode(texts, convert_to_tensor=False, batch_size=settings.BATCH_SIZE)
        return embeddings.tolist()
    
    async def close(self):
        """Close connections"""
        await self.ollama_client.aclose()
