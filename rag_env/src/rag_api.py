from .paths_config import HR_POLICY_FILE_1, HR_POLICY_FILE_2, INDEX_DIR
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from .hr_policy_rag import HRPolicyRAG
from .utilities import Decorators, Strings
from .logger_config import logger
from .DTO import QueryRequest, QueryResponse, DocumentSource
import os
from contextlib import asynccontextmanager

# Global RAG instance hold the RAG class instance for shared access in the app
rag = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and clean up resources"""
    global rag  #to make it accessible in the app
    try:
        # Init RAG
        rag = HRPolicyRAG(
            file_paths=[
                HR_POLICY_FILE_1,
                HR_POLICY_FILE_2
            ],
            index_path=INDEX_DIR
        )
        logger.info("RAG system initialized with files: %s", rag.file_paths)
        # Load vectorstore
        rag.load_vectorstore()

        logger.info("RAG system initialized successfully")
        yield
    except Exception as e:
        logger.error("Failed to initialize RAG system: %s", e)
        raise
    finally:
        # Cleanup resources
        if rag:
            logger.info("Cleaning up RAG resources")

app = FastAPI(lifespan=lifespan)

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
@Decorators.time_it
def ask_question(
    request: QueryRequest,
    rag: HRPolicyRAG = Depends(get_rag) #dependency injection
):
    try:
        # Process query
        result = rag.generate_adaptive_answer(request.question)
        sources = []
        for doc in result.get("source_documents", []):
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", 0)
            sources.append(DocumentSource(
                content=doc.page_content[:Strings.max_content_length] + "..." if len(doc.page_content) > Strings.max_content_length else doc.page_content,
                source=source,
                page=page
            ))

        return QueryResponse(
            question=request.question,
            answer=result["result"],
            confidence=result.get("confidence", 0.0),
            sources=sources
        )
    except Exception as e:
        logger.exception(f"Error processing question: {request.question}")
        raise HTTPException(500, "Internal server error") from e

@app.get("/")
def read_root():
    return {"message": "RAG API is running!"}