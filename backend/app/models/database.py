"""
database.py — SQLAlchemy Models & Database Setup

Defines three core tables:
  1. documents     — metadata about uploaded files
  2. document_chunks — text chunks with vector embeddings (pgvector)
  3. audit_logs    — compliance trail of every LLM interaction

The init_db() function creates the pgvector extension and all tables.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Text,
    DateTime, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pgvector.sqlalchemy import Vector

from app.config import settings

# ──────────────────────────────────────────────
# Engine & Session
# ──────────────────────────────────────────────
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session.
    Automatically closes the session when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ──────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────

class Document(Base):
    """
    Stores metadata about each uploaded document.
    One document has many chunks.
    """
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)        # pdf, docx, txt
    file_size_bytes = Column(Integer)
    chunk_count = Column(Integer, default=0)               # How many chunks were created
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="processing")      # processing, ready, error

    # Relationship: a document has many chunks
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document {self.filename} ({self.status})>"


class DocumentChunk(Base):
    """
    Stores individual text chunks and their vector embeddings.
    The 'embedding' column uses pgvector's Vector type for similarity search.
    """
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)          # Position within the document
    content = Column(Text, nullable=False)                 # The actual text of the chunk
    page_number = Column(Integer, nullable=True)           # Source page (if applicable)
    # NOTE: Vector dimension must match your embedding model's output.
    # - OpenAI text-embedding-3-small → 1536 dimensions
    # - Ollama nomic-embed-text       → 768 dimensions
    # If you switch providers, you must re-upload documents to re-embed them.
    embedding = Column(Vector(settings.EMBEDDING_DIMENSIONS))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to the parent document
    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<Chunk {self.chunk_index} of doc {self.document_id}>"


class AuditLog(Base):
    """
    Records every LLM interaction for compliance and audit purposes.
    Captures the full pipeline: query → retrieved context → prompt → response.
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action_type = Column(String(50), nullable=False)       # chat_query, report_summary, etc.
    user_query = Column(Text)                              # What the user asked
    retrieved_chunk_ids = Column(JSON, default=list)       # IDs of chunks used as context
    llm_prompt = Column(Text)                              # Full prompt sent to the LLM
    llm_response = Column(Text)                            # What the LLM returned
    model_used = Column(String(100))                       # e.g., gpt-4
    tokens_used = Column(Integer, nullable=True)           # Total token consumption
    response_time_ms = Column(Float, nullable=True)        # Latency in milliseconds

    def __repr__(self):
        return f"<AuditLog {self.action_type} at {self.timestamp}>"


# ──────────────────────────────────────────────
# Database Initialization
# ──────────────────────────────────────────────

def init_db():
    """
    Creates the pgvector extension (if not exists) and all tables.
    Called once on application startup.
    """
    from sqlalchemy import text

    with engine.connect() as conn:
        # Enable the pgvector extension for vector similarity search
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    # Create all tables defined above
    Base.metadata.create_all(bind=engine)
