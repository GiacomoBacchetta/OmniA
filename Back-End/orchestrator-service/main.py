from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Optional, List, Dict
import uuid
import logging
import redis.asyncio as redis

from config import settings
from services.agent_registry import AgentRegistry
from services.query_processor import QueryProcessor
from schemas import QueryRequest, QueryResponse, AgentRegistration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize services
redis_client: Optional[redis.Redis] = None
agent_registry: Optional[AgentRegistry] = None
query_processor: Optional[QueryProcessor] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global redis_client, agent_registry, query_processor
    
    redis_client = await redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
        encoding="utf-8",
        decode_responses=True
    )
    
    agent_registry = AgentRegistry(redis_client)
    query_processor = QueryProcessor(agent_registry)
    
    yield
    
    # Shutdown
    if redis_client:
        await redis_client.close()


app = FastAPI(
    title="OmniA Orchestrator Service",
    description="Agentic RAG orchestrator for intelligent query routing",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "service": "OmniA Orchestrator Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "redis": "unknown"
    }
    
    try:
        await redis_client.ping()
        health_status["redis"] = "healthy"
    except Exception as e:
        health_status["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a user query using agentic RAG
    
    The orchestrator will:
    1. Analyze the query
    2. Determine which field agent(s) to invoke
    3. Gather responses from agents
    4. Synthesize final response
    """
    try:
        query_id = str(uuid.uuid4())
        logger.info(f"[QUERY {query_id}] Received query: {request.query[:100]}...")
        logger.debug(f"[QUERY {query_id}] Fields: {request.fields}, Max results: {request.max_results}")
        
        # Process query through orchestrator
        result = await query_processor.process_query(
            query_id=query_id,
            query_text=request.query,
            fields=request.fields,
            max_results=request.max_results
        )
        
        logger.info(f"[QUERY {query_id}] Processed successfully. Agents consulted: {result.get('agents_consulted', [])}")
        
        return QueryResponse(
            query_id=query_id,
            query=request.query,
            response=result["response"],
            sources=result.get("sources", []),
            agents_consulted=result.get("agents_consulted", []),
            processing_time_ms=result.get("processing_time_ms", 0)
        )
    
    except Exception as e:
        logger.error(f"[QUERY {query_id}] Processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}"
        )


@app.get("/api/v1/query/{query_id}")
async def get_query_status(query_id: str):
    """Get status of a query (for async processing in future)"""
    # Placeholder for async query tracking
    return {"query_id": query_id, "status": "completed"}


@app.post("/api/v1/agents/register", status_code=status.HTTP_201_CREATED)
async def register_agent(registration: AgentRegistration):
    """
    Register a new field-specific agent
    
    Agents register themselves on startup
    """
    try:
        await agent_registry.register_agent(
            field=registration.field,
            agent_url=registration.agent_url,
            capabilities=registration.capabilities
        )
        return {"message": f"Agent registered for field: {registration.field}"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.delete("/api/v1/agents/{field}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_agent(field: str):
    """Unregister an agent"""
    await agent_registry.unregister_agent(field)
    return None


@app.get("/api/v1/agents")
async def list_agents():
    """List all registered agents"""
    agents = await agent_registry.list_agents()
    return {"agents": agents}


@app.get("/api/v1/agents/{field}")
async def get_agent_info(field: str):
    """Get information about a specific agent"""
    try:
        agent = await agent_registry.get_agent(field)
        return agent
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent not found for field: {field}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
