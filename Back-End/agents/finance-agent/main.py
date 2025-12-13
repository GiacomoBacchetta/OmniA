import asyncio
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import httpx

from config import settings
from services.rag_service import RAGService
from schemas import QueryRequest, QueryResponse


# Initialize services
rag_service = RAGService()


async def register_with_orchestrator():
    """Register this agent with the orchestrator"""
    if not settings.AUTO_REGISTER:
        return
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.ORCHESTRATOR_URL}/api/v1/agents/register",
                json={
                    "field": settings.FIELD_NAME,
                    "agent_url": f"http://{settings.SERVICE_NAME}:{settings.PORT}",
                    "capabilities": {
                        "max_results": settings.TOP_K_RESULTS,
                        "score_threshold": settings.SCORE_THRESHOLD
                    }
                }
            )
            response.raise_for_status()
            print(f"Successfully registered with orchestrator for field: {settings.FIELD_NAME}")
    except Exception as e:
        print(f"Failed to register with orchestrator: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await rag_service.initialize()
    await register_with_orchestrator()
    
    yield
    
    # Shutdown
    await rag_service.close()


app = FastAPI(
    title=f"OmniA Field Agent - {settings.FIELD_NAME}",
    description=f"RAG agent for {settings.FIELD_NAME} field",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "service": f"OmniA Field Agent",
        "field": settings.FIELD_NAME,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "field": settings.FIELD_NAME
    }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Process a query for this field using RAG
    """
    try:
        result = await rag_service.process_query(
            query=request.query,
            max_results=request.max_results or settings.TOP_K_RESULTS
        )
        
        return QueryResponse(
            field=settings.FIELD_NAME,
            answer=result["answer"],
            sources=result["sources"],
            confidence=result.get("confidence", 0.0)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
