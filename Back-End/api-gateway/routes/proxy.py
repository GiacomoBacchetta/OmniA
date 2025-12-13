from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
import httpx
import logging
from config import settings

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


async def proxy_request(target_url: str, request: Request):
    """Proxy request to target service"""
    logger.debug(f"[PROXY] Starting proxy request to: {target_url}")
    logger.debug(f"[PROXY] Method: {request.method}, Headers count: {len(request.headers)}")
    
    # Use longer timeout for query endpoints (Ollama can be slow)
    timeout = 180.0 if "/query" in target_url else 30.0
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            # Forward the request
            logger.debug(f"[PROXY] Forwarding request to target service")
            response = await client.request(
                method=request.method,
                url=target_url,
                headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
                content=await request.body(),
            )
            
            logger.info(f"[PROXY] Received response: status={response.status_code}, content-type={response.headers.get('content-type')}")
            
            # Return the response
            return StreamingResponse(
                response.aiter_bytes(),
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        except httpx.RequestError as e:
            logger.error(f"[PROXY] Request failed to {target_url}: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: {str(e)}"
            )


# Archive Service Routes
# Specific routes must come BEFORE catch-all routes
@router.get("/archive/items")
async def archive_items_proxy(request: Request):
    """Proxy requests to archive items list"""
    logger.info(f"[ARCHIVE ITEMS] Fetching archive items list")
    logger.debug(f"[ARCHIVE ITEMS] Client: {request.client.host}")
    
    query_params = str(request.url.query)
    target_url = f"{settings.ARCHIVE_SERVICE_URL}/api/v1/archive/items"
    if query_params:
        target_url += f"?{query_params}"
        logger.debug(f"[ARCHIVE ITEMS] Query parameters: {query_params}")
    
    logger.info(f"[ARCHIVE ITEMS] Forwarding to: {target_url}")
    return await proxy_request(target_url, request)


@router.get("/archive/map/all")
async def archive_map_proxy(request: Request):
    """Proxy requests to archive map"""
    logger.info(f"[ARCHIVE MAP] Fetching all archive locations")
    logger.debug(f"[ARCHIVE MAP] Client: {request.client.host}")
    
    query_params = str(request.url.query)
    target_url = f"{settings.ARCHIVE_SERVICE_URL}/api/v1/archive/map/all"
    if query_params:
        target_url += f"?{query_params}"
        logger.debug(f"[ARCHIVE MAP] Query parameters: {query_params}")
    
    logger.info(f"[ARCHIVE MAP] Forwarding to: {target_url}")
    return await proxy_request(target_url, request)


@router.delete("/archive/{item_id}")
async def delete_archive_item_proxy(item_id: str, request: Request):
    """Proxy delete requests to archive service"""
    logger.info(f"[ARCHIVE DELETE] Deleting item: {item_id}")
    logger.debug(f"[ARCHIVE DELETE] Client: {request.client.host}")
    
    target_url = f"{settings.ARCHIVE_SERVICE_URL}/api/v1/archive/{item_id}"
    logger.info(f"[ARCHIVE DELETE] Forwarding to: {target_url}")
    return await proxy_request(target_url, request)


@router.put("/archive/{item_id}")
async def update_archive_item_proxy(item_id: str, request: Request):
    """Proxy update requests to archive service"""
    logger.info(f"[ARCHIVE UPDATE] Updating item: {item_id}")
    logger.debug(f"[ARCHIVE UPDATE] Client: {request.client.host}")
    
    target_url = f"{settings.ARCHIVE_SERVICE_URL}/api/v1/archive/{item_id}"
    logger.info(f"[ARCHIVE UPDATE] Forwarding to: {target_url}")
    return await proxy_request(target_url, request)


@router.get("/files/{field}/{filename:path}")
async def files_proxy(field: str, filename: str, request: Request):
    """Proxy file requests to archive service"""
    logger.info(f"[FILES] Serving file: {field}/{filename}")
    logger.debug(f"[FILES] Client: {request.client.host}")
    
    target_url = f"{settings.ARCHIVE_SERVICE_URL}/api/v1/files/{field}/{filename}"
    logger.info(f"[FILES] Forwarding to: {target_url}")
    return await proxy_request(target_url, request)


@router.api_route("/archive/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def archive_proxy(path: str, request: Request):
    """Proxy requests to archive service (catch-all)"""
    logger.info(f"[ARCHIVE PROXY] {request.method} request to path: /{path}")
    logger.debug(f"[ARCHIVE PROXY] Client: {request.client.host}")
    
    target_url = f"{settings.ARCHIVE_SERVICE_URL}/api/v1/archive/{path}"
    logger.info(f"[ARCHIVE PROXY] Forwarding to: {target_url}")
    return await proxy_request(target_url, request)


# Orchestrator Service Routes
@router.api_route("/query/{path:path}", methods=["GET", "POST"])
async def orchestrator_proxy(path: str, request: Request):
    """Proxy requests to orchestrator service"""
    logger.info(f"[ORCHESTRATOR PROXY] {request.method} request to path: /{path}")
    logger.debug(f"[ORCHESTRATOR PROXY] Client: {request.client.host}")
    
    target_url = f"{settings.ORCHESTRATOR_SERVICE_URL}/api/v1/query/{path}"
    logger.info(f"[ORCHESTRATOR PROXY] Forwarding to: {target_url}")
    return await proxy_request(target_url, request)


@router.api_route("/query", methods=["POST"])
async def query_proxy(request: Request):
    """Proxy query requests to orchestrator service"""
    logger.info(f"[QUERY] Received query request")
    logger.debug(f"[QUERY] Client: {request.client.host}")
    
    target_url = f"{settings.ORCHESTRATOR_SERVICE_URL}/api/v1/query"
    logger.info(f"[QUERY] Forwarding to orchestrator: {target_url}")
    return await proxy_request(target_url, request)


# Vector DB Service Routes (admin access)
@router.api_route("/index/{path:path}", methods=["GET", "POST", "DELETE"])
async def vector_db_proxy(path: str, request: Request):
    """Proxy requests to vector db service"""
    logger.info(f"[VECTOR DB PROXY] {request.method} request to path: /{path}")
    logger.debug(f"[VECTOR DB PROXY] Client: {request.client.host}")
    
    target_url = f"{settings.VECTOR_DB_SERVICE_URL}/api/v1/index/{path}"
    logger.info(f"[VECTOR DB PROXY] Forwarding to: {target_url}")
    return await proxy_request(target_url, request)


# Map View Route
@router.api_route("/map", methods=["GET", "POST", "PUT", "DELETE"])
async def map_view(request: Request):
    """Proxy to archive service map/all endpoint"""
    logger.info(f"[MAP VIEW] Incoming request from {request.client.host}")
    
    query_params = str(request.url.query)
    target_url = f"{settings.ARCHIVE_SERVICE_URL}/api/v1/archive/map/all"
    if query_params:
        target_url += f"?{query_params}"
        logger.debug(f"[MAP VIEW] Query parameters: {query_params}")
    
    logger.info(f"[MAP VIEW] Proxying request to: {target_url}")
    return await proxy_request(target_url, request)