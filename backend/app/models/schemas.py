"""
schemas.py — Pydantic Request/Response Models

These schemas validate all API inputs and structure all outputs.
FastAPI uses them automatically for request parsing, response
serialization, and OpenAPI documentation generation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# Document Schemas
# ──────────────────────────────────────────────

class DocumentResponse(BaseModel):
    """Returned after uploading a document or when listing documents."""
    id: UUID
    filename: str
    file_type: str
    file_size_bytes: Optional[int] = None
    chunk_count: int
    uploaded_at: datetime
    status: str

    class Config:
        from_attributes = True  # Allows creating from SQLAlchemy model instances


# ──────────────────────────────────────────────
# Chat / RAG Schemas
# ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    """User's question to the RAG system."""
    query: str = Field(..., min_length=1, max_length=2000, description="The question to ask")
    document_ids: Optional[list[UUID]] = Field(
        default=None,
        description="Optional: limit search to specific documents. If empty, searches all."
    )

class SourceChunk(BaseModel):
    """A single retrieved chunk shown as a source reference."""
    chunk_id: UUID
    document_name: str
    content_preview: str = Field(..., description="First 200 chars of the chunk")
    relevance_score: float

class ChatResponse(BaseModel):
    """RAG response with the answer and its source references."""
    answer: str
    sources: list[SourceChunk]
    query: str
    model_used: str


# ──────────────────────────────────────────────
# Report Schemas
# ──────────────────────────────────────────────

class ReportRequest(BaseModel):
    """Request to generate a report from indexed documents."""
    report_type: str = Field(
        ...,
        description="Type of report: 'summary', 'risk_note', or 'client_email'"
    )
    document_ids: Optional[list[UUID]] = Field(
        default=None,
        description="Documents to include. If empty, uses all documents."
    )
    additional_instructions: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Extra context or instructions for the report"
    )

class ReportResponse(BaseModel):
    """Generated report content."""
    report_type: str
    content: str
    sources_used: int
    model_used: str


# ──────────────────────────────────────────────
# Audit Log Schemas
# ──────────────────────────────────────────────

class AuditLogResponse(BaseModel):
    """A single audit log entry."""
    id: UUID
    timestamp: datetime
    action_type: str
    user_query: Optional[str]
    llm_response: Optional[str]
    model_used: Optional[str]
    tokens_used: Optional[int]
    response_time_ms: Optional[float]

    class Config:
        from_attributes = True
