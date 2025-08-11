from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    question: str

class DocumentSource(BaseModel):
    content: str
    source: str
    page: int

class QueryResponse(BaseModel):
    question: str
    answer: str
    processingTimeMs: int = 0
    confidence: float = None
    sources: List[DocumentSource] = []