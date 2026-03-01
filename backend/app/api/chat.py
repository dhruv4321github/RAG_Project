"""
chat.py — RAG Chat / Query API Routes

Endpoints:
  POST /api/chat/query   — Ask a question and get a RAG-grounded answer
  GET  /api/chat/history  — Get recent chat interactions from the audit log
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_pipeline import generate_response
from app.services.audit_logger import get_audit_logs
from app.utils.security import sanitize_input

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
def query_documents(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Ask a question about uploaded documents.

    The RAG pipeline:
    1. Embeds your question as a vector
    2. Finds the most relevant document chunks via similarity search
    3. Sends the question + context to the LLM
    4. Returns a grounded answer with source references

    You can optionally specify document_ids to limit the search scope
    to specific documents (useful when an advisor has multiple clients).
    """
    # Sanitize user input for safety
    clean_query = sanitize_input(request.query)

    if not clean_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        result = generate_response(
            db=db,
            query=clean_query,
            document_ids=request.document_ids,
        )
        return ChatResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/history")
def get_chat_history(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Retrieve recent chat interactions from the audit log.
    Useful for reviewing past questions and answers in the current session.
    """
    logs = get_audit_logs(db, limit=limit, offset=offset, action_type="chat_query")

    return [
        {
            "id": str(log.id),
            "timestamp": log.timestamp.isoformat(),
            "query": log.user_query,
            "response": log.llm_response,
            "model": log.model_used,
            "tokens": log.tokens_used,
            "response_time_ms": log.response_time_ms,
        }
        for log in logs
    ]
