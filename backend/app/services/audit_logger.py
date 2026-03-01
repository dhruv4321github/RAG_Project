"""
audit_logger.py — Compliance Audit Logging

Logs every LLM interaction to the database for regulatory compliance.
In financial services, it's critical to maintain a complete record of:
  - What was asked
  - What context was retrieved
  - What prompt was sent to the AI
  - What the AI responded
  - Performance metrics (tokens, latency)

This audit trail enables compliance officers to review any AI-generated
content and ensures accountability.
"""

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.database import AuditLog


def log_interaction(
    db: Session,
    action_type: str,
    user_query: Optional[str] = None,
    retrieved_chunk_ids: Optional[list[str]] = None,
    llm_prompt: Optional[str] = None,
    llm_response: Optional[str] = None,
    model_used: Optional[str] = None,
    tokens_used: Optional[int] = None,
    response_time_ms: Optional[float] = None,
) -> AuditLog:
    """
    Creates an audit log entry for any LLM interaction.

    Args:
        db: Database session
        action_type: Category of action (e.g., "chat_query", "report_summary")
        user_query: The original question or request from the advisor
        retrieved_chunk_ids: IDs of document chunks used as context
        llm_prompt: The full prompt sent to the LLM (system + context + query)
        llm_response: The LLM's generated response
        model_used: Which model was used (e.g., "gpt-4")
        tokens_used: Total tokens consumed (prompt + completion)
        response_time_ms: End-to-end latency in milliseconds

    Returns:
        The created AuditLog record
    """
    log_entry = AuditLog(
        id=uuid.uuid4(),
        action_type=action_type,
        user_query=user_query,
        retrieved_chunk_ids=retrieved_chunk_ids or [],
        llm_prompt=llm_prompt,
        llm_response=llm_response,
        model_used=model_used,
        tokens_used=tokens_used,
        response_time_ms=response_time_ms,
    )

    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    return log_entry


def get_audit_logs(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    action_type: Optional[str] = None,
) -> list[AuditLog]:
    """
    Retrieves audit log entries, ordered by most recent first.
    Optionally filters by action type.

    Args:
        db: Database session
        limit: Maximum number of entries to return
        offset: Number of entries to skip (for pagination)
        action_type: Optional filter (e.g., "chat_query" only)

    Returns:
        List of AuditLog records
    """
    query = db.query(AuditLog)

    if action_type:
        query = query.filter(AuditLog.action_type == action_type)

    return (
        query
        .order_by(AuditLog.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
