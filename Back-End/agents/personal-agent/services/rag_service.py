import httpx
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import os

from config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class RAGService:
    """Retrieval-Augmented Generation service for field-specific queries"""
    
    def __init__(self):
        self.embedding_model = None
        self.vector_db_client = None
        self.ollama_client = None
    
    async def initialize(self):
        """Initialize models and clients"""
        # Initialize embedding model
        os.makedirs(settings.HF_CACHE_DIR, exist_ok=True)
        self.embedding_model = SentenceTransformer(
            settings.HF_MODEL,
            cache_folder=settings.HF_CACHE_DIR
        )
        
        # Initialize HTTP clients
        self.vector_db_client = httpx.AsyncClient(
            base_url=settings.VECTOR_DB_SERVICE_URL,
            timeout=30.0
        )
        self.ollama_client = httpx.AsyncClient(
            base_url=settings.OLLAMA_URL,
            timeout=60.0
        )
        
        print(f"RAG Service initialized for field: {settings.FIELD_NAME}")
    
    async def process_query(self, query: str, max_results: int) -> Dict:
        """
        Process a query using RAG
        
        Steps:
        1. Generate query embedding
        2. Search vector DB for relevant content
        3. Build context from retrieved sources
        4. Generate answer using LLM
        """
        # Step 1: Generate query embedding
        query_embedding = self._generate_query_embedding(query)
        
        logger.info(f"Generated query embedding of length {len(query_embedding)}")
        
        # Step 2: Search vector DB
        sources = await self._search_vector_db(query_embedding, max_results)
        
        if not sources:
            return {
                "answer": f"I don't have any information in the {settings.FIELD_NAME} field to answer your question.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Step 3: Build context
        context = self._build_context(sources)
        
        # Step 4: Generate answer
        answer = await self._generate_answer(query, context)
        
        # Calculate confidence based on source scores
        confidence = self._calculate_confidence(sources)
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence
        }
    
    def _generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for the query"""
        embedding = self.embedding_model.encode(query, convert_to_tensor=False)
        embedding_list = embedding.tolist()
        
        # Pad or truncate to match expected dimension (768)
        target_dim = 768
        if len(embedding_list) < target_dim:
            # Pad with zeros
            embedding_list.extend([0.0] * (target_dim - len(embedding_list)))
        elif len(embedding_list) > target_dim:
            # Truncate
            embedding_list = embedding_list[:target_dim]
        
        return embedding_list
    
    async def _search_vector_db(
        self,
        query_embedding: List[float],
        max_results: int
    ) -> List[Dict]:
        """Search vector database for relevant content"""
        try:
            response = await self.vector_db_client.post(
                f"/api/v1/index/{settings.FIELD_NAME}/search",
                json={
                    "vector": query_embedding,
                    "limit": max_results,
                    "score_threshold": settings.SCORE_THRESHOLD
                }
            )
            response.raise_for_status()
            results = response.json()
            
            logger.info(f"Vector DB returned:  {results}")
            
            # Format sources
            sources = []
            for result in results:
                sources.append({
                    "id": result["id"],
                    "content": result["payload"].get("content", ""),
                    "score": result["score"],
                    "metadata": result["payload"].get("metadata", {})
                })
            
            return sources
        
        except Exception as e:
            print(f"Vector search failed: {e}")
            return []
    
    def _build_context(self, sources: List[Dict]) -> str:
        """Build context string from sources"""
        context_parts = []
        current_length = 0
        
        for source in sources:
            content = source["content"]
            
            # Truncate if needed
            if current_length + len(content) > settings.MAX_CONTEXT_LENGTH:
                remaining = settings.MAX_CONTEXT_LENGTH - current_length
                if remaining > 100:  # Only add if meaningful
                    context_parts.append(content[:remaining] + "...")
                break
            
            context_parts.append(content)
            current_length += len(content)
        
        return "\n\n".join(context_parts)
    
    async def _generate_answer(self, query: str, context: str) -> str:
        """Generate answer using LLM"""
        prompt = self._build_prompt(query, context)
        
        try:
            response = await self.ollama_client.post(
                "/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "Unable to generate answer")
        
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return f"Error generating answer: {str(e)}"
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Build prompt for LLM"""
        return f"""You are a helpful AI assistant with access to information from the user's {settings.FIELD_NAME} archive.

Context from {settings.FIELD_NAME}:
{context}

User Question: {query}

Based on the context above, provide a helpful and accurate answer. If the context doesn't contain enough information to fully answer the question, say so clearly."""
    
    def _calculate_confidence(self, sources: List[Dict]) -> float:
        """Calculate confidence score based on source relevance"""
        if not sources:
            return 0.0
        
        # Use average of top 3 scores
        top_scores = [s["score"] for s in sources[:3]]
        return sum(top_scores) / len(top_scores)
    
    async def close(self):
        """Close connections"""
        if self.vector_db_client:
            await self.vector_db_client.aclose()
        if self.ollama_client:
            await self.ollama_client.aclose()
