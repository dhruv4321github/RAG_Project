"""
documents.py — Document Upload & Management API Routes

Endpoints:
  POST /api/documents/upload  — Upload and process a new document
  GET  /api/documents/        — List all uploaded documents
  GET  /api/documents/{id}    — Get a specific document's metadata
  DELETE /api/documents/{id}  — Delete a document and its embeddings
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db, Document
from app.models.schemas import DocumentResponse
from app.services.document_processor import process_document
from app.utils.security import validate_file, validate_file_size, save_upload_file

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(..., description="PDF, DOCX, or TXT file to upload"),
    db: Session = Depends(get_db),
):
    """
    Upload a document for indexing.

    The document goes through the full ingestion pipeline:
    1. Validation (type, size)
    2. Text extraction (PDF/DOCX/TXT parsing)
    3. Chunking (split into overlapping segments)
    4. Embedding (convert chunks to vectors)
    5. Storage (save to PostgreSQL/pgvector)

    Returns the document metadata including chunk count and status.
    """
    # Validate file type
    file_type = validate_file(file)

    # Validate file size
    file_size = await validate_file_size(file)

    # Save to disk temporarily for processing
    content = await file.read()
    file_path = save_upload_file(content, f"{uuid.uuid4()}_{file.filename}")

    try:
        # Run the full ingestion pipeline
        doc = process_document(
            db=db,
            file_path=file_path,
            filename=file.filename,
            file_type=file_type,
            file_size=file_size,
        )
        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.get("/", response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
):
    """
    List all uploaded documents, optionally filtered by status.
    Status values: "processing", "ready", "error"
    """
    query = db.query(Document)
    if status:
        query = query.filter(Document.status == status)
    return query.order_by(Document.uploaded_at.desc()).all()


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get metadata for a specific document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Delete a document and all its associated chunks/embeddings.
    The CASCADE relationship in the database model handles chunk deletion automatically.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(doc)
    db.commit()
