"""
rag_pipeline.py — Core RAG (Retrieval-Augmented Generation) Pipeline

This is the heart of the application. When a user asks a question:
  1. Embed the query into a vector
  2. Search pgvector for the most relevant document chunks
  3. Build a prompt with the retrieved context
  4. Send to the LLM for a grounded response
  5. Log everything for audit compliance
  6. Return the answer with source references

The key principle: the LLM only answers based on the retrieved documents,
not from its general training data. This ensures factual, traceable answers.
"""

import time
import uuid
from typing import Optional

from openai import OpenAI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.models.database import DocumentChunk, Document
from app.services.audit_logger import log_interaction

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ──────────────────────────────────────────────
# System Prompt
# Defines the assistant's role and constraints.
# The assistant is instructed to ONLY use the provided
# context — never its general knowledge.
# ──────────────────────────────────────────────
SYSTEM_PROMPT = """You are an AI assistant for financial advisors. Your role is to help
advisors answer questions about their clients' financial documents accurately and safely.

CRITICAL RULES:
1. ONLY answer based on the provided document context below.
2. If the context does not contain enough information to answer, say:
   "I don't have enough information in the uploaded documents to answer this question."
3. Always cite which document and section your answer comes from.
4. Never make up financial figures, dates, or facts.
5. If you identify any potential compliance concerns, flag them clearly.
6. Use professional financial language appropriate for advisor-to-advisor communication.

DOCUMENT CONTEXT:
{context}
"""


def embed_query(query: str) -> list[float]:
    """
    Converts the user's question into a vector embedding.
    Uses the same model that was used to embed the document chunks,
    ensuring they exist in the same vector space for accurate comparison.
    """
    response = client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=[query],
    )
    return response.data[0].embedding


def retrieve_relevant_chunks(
    db: Session,
    query_embedding: list[float],
    document_ids: Optional[list[uuid.UUID]] = None,
    top_k: int = None,
) -> list[dict]:
    """
    Performs similarity search using pgvector's cosine distance operator (<=>).

    How it works:
    - pgvector computes the cosine distance between the query vector and every
      stored chunk vector
    - Results are ordered by distance (lower = more similar)
    - We return the top-K most relevant chunks

    If document_ids are provided, we filter to only search within those documents.
    This allows advisors to scope queries to specific client files.
    """
    if top_k is None:
        top_k = settings.TOP_K_RESULTS

    # Convert embedding to the format pgvector expects
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    # Build the SQL query with pgvector's cosine distance operator
    # The <=> operator computes cosine distance (0 = identical, 2 = opposite)
    if document_ids:
        # Filter to specific documents
        placeholders = ",".join(f"'{str(did)}'" for did in document_ids)
        sql = text(f"""
            SELECT
                dc.id,
                dc.document_id,
                dc.content,
                dc.page_number,
                dc.chunk_index,
                d.filename,
                dc.embedding <=> :embedding AS distance
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE dc.document_id IN ({placeholders})
            ORDER BY dc.embedding <=> :embedding
            LIMIT :top_k
        """)
    else:
        # Search all documents
        sql = text("""
            SELECT
                dc.id,
                dc.document_id,
                dc.content,
                dc.page_number,
                dc.chunk_index,
                d.filename,
                dc.embedding <=> :embedding AS distance
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            ORDER BY dc.embedding <=> :embedding
            LIMIT :top_k
        """)

    result = db.execute(sql, {"embedding": embedding_str, "top_k": top_k})
    rows = result.fetchall()

    # Convert to list of dicts for easier handling
    chunks = []
    for row in rows:
        chunks.append({
            "chunk_id": row[0],
            "document_id": row[1],
            "content": row[2],
            "page_number": row[3],
            "chunk_index": row[4],
            "filename": row[5],
            "distance": row[6],
            "relevance_score": 1 - row[6],  # Convert distance to similarity (0-1)
        })

    return chunks


def build_prompt(query: str, chunks: list[dict]) -> str:
    """
    Assembles the full prompt for the LLM.

    Structure:
    - System message with role definition and rules
    - Retrieved document context (numbered for citation)
    - The user's question

    Numbering the context chunks makes it easy for the LLM to cite
    specific sources in its response.
    """
    # Format each chunk with its source info for citation
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i} — {chunk['filename']}, Page {chunk['page_number']}]\n"
            f"{chunk['content']}"
        )

    context = "\n\n---\n\n".join(context_parts)
    system = SYSTEM_PROMPT.format(context=context)

    return system


def generate_response(
    db: Session,
    query: str,
    document_ids: Optional[list[uuid.UUID]] = None,
) -> dict:
    """
    Full RAG pipeline execution:
      1. Embed the query
      2. Retrieve relevant chunks from pgvector
      3. Build the prompt with context
      4. Call the LLM
      5. Log everything
      6. Return structured response

    Returns a dict with: answer, sources, query, model_used
    """
    start_time = time.time()

    # Step 1: Embed the query
    query_embedding = embed_query(query)

    # Step 2: Retrieve relevant chunks
    chunks = retrieve_relevant_chunks(db, query_embedding, document_ids)

    if not chunks:
        return {
            "answer": "No relevant documents were found. Please upload documents first.",
            "sources": [],
            "query": query,
            "model_used": settings.OPENAI_MODEL,
        }

    # Step 3: Build the prompt
    system_prompt = build_prompt(query, chunks)

    # Step 4: Call the LLM
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        temperature=0.1,  # Low temperature for factual, consistent answers
        max_tokens=2000,
    )

    answer = response.choices[0].message.content
    tokens_used = response.usage.total_tokens if response.usage else None

    # Step 5: Calculate response time
    response_time_ms = (time.time() - start_time) * 1000

    # Step 6: Log for audit
    log_interaction(
        db=db,
        action_type="chat_query",
        user_query=query,
        retrieved_chunk_ids=[str(c["chunk_id"]) for c in chunks],
        llm_prompt=system_prompt,
        llm_response=answer,
        model_used=settings.OPENAI_MODEL,
        tokens_used=tokens_used,
        response_time_ms=response_time_ms,
    )

    # Step 7: Build source references
    sources = [
        {
            "chunk_id": str(c["chunk_id"]),
            "document_name": c["filename"],
            "content_preview": c["content"][:200] + "..." if len(c["content"]) > 200 else c["content"],
            "relevance_score": round(c["relevance_score"], 4),
        }
        for c in chunks
    ]

    return {
        "answer": answer,
        "sources": sources,
        "query": query,
        "model_used": settings.OPENAI_MODEL,
    }
