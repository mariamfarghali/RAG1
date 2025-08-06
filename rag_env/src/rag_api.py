from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from .hr_policy_rag import HRPolicyRAG
import os
import time
import logging
from contextlib import asynccontextmanager
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global RAG instance
rag = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and clean up resources"""
    global rag
    try:
        # Setup paths dynamically
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "..", "data")
        index_dir = os.path.join(base_dir, "..", "hr_faiss_index")
        # Init RAG
        rag = HRPolicyRAG(
            file_paths=[
                os.path.join(data_dir, "HR_Policy_Dataset1.txt"),
                os.path.join(data_dir, "HR_Policy_Dataset2.txt"),
            ],
            index_path=index_dir
        )
        # Load vectorstore
        rag.load_vectorstore()
        logger.info("RAG system initialized successfully")
        yield
    except Exception as e:
        logger.exception("Failed to initialize RAG system")
        raise
    finally:
        # Cleanup resources if needed
        if rag:
            logger.info("Cleaning up RAG resources")
            # Add any cleanup logic here

app = FastAPI(lifespan=lifespan)

class QueryRequest(BaseModel):
    question: str

class DocumentSource(BaseModel):
    content: str
    source: str
    page: int

class QueryResponse(BaseModel):
    question: str
    answer: str
    processing_time_ms: int
    confidence: float = None
    sources: List[DocumentSource] = []

def get_rag() -> HRPolicyRAG:
    if rag is None:
        raise HTTPException(503, "RAG system not initialized")
    return rag

@app.get("/health")
def health_check():
    return {
        "status": "OK",
        "rag_initialized": rag is not None
    }

@app.post("/query")
def ask_question(
    request: QueryRequest, 
    rag: HRPolicyRAG = Depends(get_rag)
):
    try:
        start_time = time.time()
        
        # Process query
        result = rag.generate_adaptive_answer(request.question)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Format sources
        sources = []
        for doc in result.get("source_documents", []):
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", 0)
            sources.append(DocumentSource(
                content=doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                source=source,
                page=page
            ))
        
        return QueryResponse(
            question=request.question,
            answer=result["result"],
            processing_time_ms=processing_time,
            confidence=result.get("confidence", 0.0),
            sources=sources
        )
    except Exception as e:
        logger.exception(f"Error processing question: {request.question}")
        raise HTTPException(500, "Internal server error") from e

@app.get("/")
def read_root():
    return {"message": "RAG API is running!"}

