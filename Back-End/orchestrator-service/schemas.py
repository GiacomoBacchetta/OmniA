from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime


class QueryRequest(BaseModel):
    query: str
    fields: Optional[List[str]] = None  # Specific fields to search, None = all
    max_results: int = 5


class QueryResponse(BaseModel):
    query_id: str
    query: str
    response: str
    sources: List[Dict]
    agents_consulted: List[str]
    processing_time_ms: float


class AgentRegistration(BaseModel):
    field: str
    agent_url: HttpUrl
    capabilities: Optional[Dict] = None
