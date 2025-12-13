from pydantic import BaseModel
from typing import List, Dict, Optional


class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = None


class Source(BaseModel):
    id: str
    content: str
    score: float
    metadata: Dict


class QueryResponse(BaseModel):
    field: str
    answer: str
    sources: List[Source]
    confidence: float
