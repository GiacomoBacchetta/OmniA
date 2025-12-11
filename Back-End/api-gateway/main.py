from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import time
from typing import Optional
import redis.asyncio as redis
from contextlib import asynccontextmanager

from config import settings
from middleware.auth import get_current_user
from middleware.rate_limit import RateLimiter
from routes import auth, proxy

# Redis connection
redis_client: Optional[redis.Redis] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global redis_client
    redis_client = await redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
        encoding="utf-8",
        decode_responses=True
    )
    yield
    # Shutdown
    if redis_client:
        await redis_client.close()


app = FastAPI(
    title="OmniA API Gateway",
    description="API Gateway for OmniA self-management application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
rate_limiter = RateLimiter(redis_client)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/")
async def root():
    return {
        "service": "OmniA API Gateway",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "redis": "unknown",
        "services": {}
    }
    
    # Check Redis
    try:
        await redis_client.ping()
        health_status["redis"] = "healthy"
    except Exception as e:
        health_status["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check downstream services
    services = {
        "archive": settings.ARCHIVE_SERVICE_URL,
        "embedding": settings.EMBEDDING_SERVICE_URL,
        "vector_db": settings.VECTOR_DB_SERVICE_URL,
        "orchestrator": settings.ORCHESTRATOR_SERVICE_URL,
    }
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in services.items():
            try:
                response = await client.get(f"{url}/health")
                health_status["services"][name] = "healthy" if response.status_code == 200 else "unhealthy"
            except Exception:
                health_status["services"][name] = "unreachable"
                health_status["status"] = "degraded"
    
    return health_status


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(
    proxy.router,
    prefix="",
    tags=["Services"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
