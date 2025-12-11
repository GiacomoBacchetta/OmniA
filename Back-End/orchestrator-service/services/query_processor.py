import httpx
import time
import logging
from typing import List, Dict, Optional
from config import settings
from services.agent_registry import AgentRegistry

logger = logging.getLogger(__name__)


class QueryProcessor:
    """Process queries using agentic RAG approach"""
    
    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry
        self.ollama_client = httpx.AsyncClient(base_url=settings.OLLAMA_URL, timeout=120.0)
    
    async def process_query(
        self,
        query_id: str,
        query_text: str,
        fields: Optional[List[str]] = None,
        max_results: int = 5
    ) -> Dict:
        """
        Process a query through the agentic RAG system
        
        Steps:
        1. Determine which fields to query (if not specified)
        2. Route query to appropriate field agents
        3. Gather responses from agents
        4. Synthesize final response using LLM
        """
        start_time = time.time()
        logger.info(f"[{query_id}] Starting query processing")
        
        # Step 1: Determine fields to query
        if not fields:
            logger.debug(f"[{query_id}] Determining relevant fields")
            fields = await self._determine_relevant_fields(query_text)
        logger.info(f"[{query_id}] Target fields: {fields}")
        
        # Step 2: Get agents for these fields
        logger.debug(f"[{query_id}] Fetching agents for fields")
        agents = await self.agent_registry.get_agents_for_fields(fields)
        logger.info(f"[{query_id}] Found {len(agents)} agents: {list(agents.keys())}")
        
        if not agents:
            logger.warning(f"[{query_id}] No agents available to answer query")
            return {
                "response": "No agents available to answer your query.",
                "sources": [],
                "agents_consulted": [],
                "processing_time_ms": (time.time() - start_time) * 1000
            }
        
        # Step 3: Query each agent
        logger.info(f"[{query_id}] Querying {len(agents)} agents")
        agent_responses = []
        for field, agent_info in agents.items():
            try:
                logger.debug(f"[{query_id}] Querying agent for field '{field}' at {agent_info['agent_url']}")
                response = await self._query_agent(
                    agent_url=agent_info["agent_url"],
                    query=query_text,
                    max_results=max_results
                )
                logger.info(f"[{query_id}] Received response from '{field}' agent")
                agent_responses.append({
                    "field": field,
                    "response": response
                })
            except Exception as e:
                logger.error(f"[{query_id}] Error querying agent for {field}: {str(e)}")
        
        # Step 4: Synthesize final response
        logger.info(f"[{query_id}] Synthesizing final response from {len(agent_responses)} agent responses")
        final_response = await self._synthesize_response(query_text, agent_responses)
        logger.debug(f"[{query_id}] Synthesis complete")
        
        # Extract sources
        sources = []
        for resp in agent_responses:
            if "sources" in resp["response"]:
                sources.extend(resp["response"]["sources"])
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "response": final_response,
            "sources": sources,
            "agents_consulted": list(agents.keys()),
            "processing_time_ms": processing_time
        }
    
    async def _determine_relevant_fields(self, query: str) -> List[str]:
        """
        Use LLM to determine which fields are relevant to the query
        
        In production, this could be more sophisticated:
        - Use embeddings to find similar past queries
        - Use classification model
        - Use keyword matching
        """
        # For now, return all available fields
        # In production, implement intelligent field selection
        agents = await self.agent_registry.list_agents()
        return [agent["field"] for agent in agents]
    
    async def _query_agent(
        self,
        agent_url: str,
        query: str,
        max_results: int
    ) -> Dict:
        """Query a specific field agent"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{agent_url}/query",
                json={
                    "query": query,
                    "max_results": max_results
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def _synthesize_response(
        self,
        query: str,
        agent_responses: List[Dict]
    ) -> str:
        """
        Synthesize final response from multiple agent responses using LLM
        """
        # Prepare context from all agent responses
        context = self._prepare_context(agent_responses)
        
        logger.debug(f"Context for synthesis: {context[:200] if context else '(empty)'}...")
        
        # Create prompt for LLM
        prompt = f"""You are a helpful AI assistant. Based on the following information retrieved from various sources, answer the user's question.

User Question: {query}

Retrieved Information:
{context}

Provide a comprehensive answer based on the information above. If the information is not sufficient, say so clearly."""
        
        try:
            # Call Ollama LLM
            logger.debug(f"Calling Ollama at {settings.OLLAMA_URL} with model {settings.OLLAMA_MODEL}")
            logger.debug(f"Prompt length: {len(prompt)} characters")
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
            logger.info(f"Ollama response generated successfully")
            return data.get("response", "Unable to generate response")
        
        except Exception as e:
            logger.error(f"Error synthesizing response with Ollama: {type(e).__name__}: {str(e)}")
            logger.warning(f"Falling back to concatenated responses")
            # Fallback: return concatenated responses
            return self._fallback_response(agent_responses)
    
    def _prepare_context(self, agent_responses: List[Dict]) -> str:
        """Prepare context from agent responses"""
        context_parts = []
        
        for resp in agent_responses:
            field = resp["field"]
            response_data = resp["response"]
            
            context_parts.append(f"\n--- Information from {field} ---")
            
            if "answer" in response_data:
                context_parts.append(response_data["answer"])
            
            if "sources" in response_data:
                context_parts.append("\nRelevant excerpts:")
                for source in response_data["sources"][:3]:  # Top 3 sources
                    if "content" in source:
                        context_parts.append(f"- {source['content'][:200]}...")
        
        return "\n".join(context_parts)
    
    def _fallback_response(self, agent_responses: List[Dict]) -> str:
        """Fallback response if LLM synthesis fails"""
        responses = []
        for resp in agent_responses:
            field = resp["field"]
            if "answer" in resp["response"]:
                responses.append(f"From {field}: {resp['response']['answer']}")
        
        return "\n\n".join(responses) if responses else "No relevant information found."
    
    async def close(self):
        """Close connections"""
        await self.ollama_client.aclose()
