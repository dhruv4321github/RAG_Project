"""
report_generator.py — Financial Report Generation

Generates three types of reports using specialized prompt templates:
  1. Portfolio Summary  — overview of holdings, allocations, performance
  2. Risk Note         — identifies risk factors and concentration issues
  3. Client Email      — professional, compliant email draft

Each report type:
  - Retrieves relevant document chunks via the RAG pipeline
  - Uses a domain-specific prompt template
  - Logs the interaction for audit compliance
"""

import time
from typing import Optional
from uuid import UUID

from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.services.rag_pipeline import embed_query, retrieve_relevant_chunks
from app.services.audit_logger import log_interaction

client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ──────────────────────────────────────────────
# Prompt Templates
# Each template is carefully designed for its specific use case.
# ──────────────────────────────────────────────

REPORT_TEMPLATES = {
    "summary": """You are a financial report writer assisting an advisor.
Based ONLY on the provided document context, generate a comprehensive portfolio summary.

Structure your summary as follows:
1. **Executive Overview** — High-level snapshot of the client's financial position
2. **Asset Allocation** — Breakdown of holdings by asset class (equities, fixed income, alternatives, cash)
3. **Key Holdings** — Notable positions and their significance
4. **Performance Notes** — Any performance data found in the documents
5. **Observations** — Important patterns or items the advisor should be aware of

If certain sections cannot be completed due to missing data, explicitly note what information
is unavailable rather than making assumptions.

DOCUMENT CONTEXT:
{context}

{additional_instructions}""",

    "risk_note": """You are a risk analyst assistant for a financial advisory firm.
Based ONLY on the provided document context, generate a risk assessment note.

Structure your analysis as follows:
1. **Risk Summary** — Overall risk profile assessment
2. **Concentration Risk** — Identify any over-concentration in sectors, asset classes, or individual positions
3. **Market Risk Factors** — External risk factors relevant to the portfolio
4. **Liquidity Concerns** — Any illiquid positions or redemption restrictions
5. **Compliance Flags** — Potential regulatory or suitability concerns
6. **Recommendations** — Suggested risk mitigation steps for the advisor to consider

Flag any areas where the documents contain insufficient data for a complete risk assessment.

DOCUMENT CONTEXT:
{context}

{additional_instructions}""",

    "client_email": """You are a communication specialist helping a financial advisor draft a client email.
Based ONLY on the provided document context, draft a professional client communication.

Requirements:
- Use a warm but professional tone appropriate for advisor-client communication
- Reference specific details from the documents to personalize the email
- Include appropriate disclaimers (e.g., "past performance does not guarantee future results")
- Do NOT include specific account numbers or sensitive identifiers
- Keep the email concise but informative
- End with a clear call to action (e.g., scheduling a review meeting)

Format:
Subject: [Appropriate subject line]

[Email body]

[Professional sign-off placeholder]

IMPORTANT DISCLAIMER: Include at the bottom:
"This communication is for informational purposes only and does not constitute investment advice.
Please consult with your advisor before making any investment decisions."

DOCUMENT CONTEXT:
{context}

{additional_instructions}""",
}


def generate_report(
    db: Session,
    report_type: str,
    document_ids: Optional[list[UUID]] = None,
    additional_instructions: Optional[str] = None,
) -> dict:
    """
    Generates a financial report by:
      1. Creating a broad retrieval query based on report type
      2. Retrieving relevant chunks from the vector store
      3. Filling the appropriate prompt template
      4. Calling the LLM for generation
      5. Logging the interaction

    Args:
        db: Database session
        report_type: One of "summary", "risk_note", "client_email"
        document_ids: Optional list of document IDs to scope the retrieval
        additional_instructions: Extra context from the advisor

    Returns:
        dict with report_type, content, sources_used, model_used
    """
    if report_type not in REPORT_TEMPLATES:
        raise ValueError(f"Unknown report type: {report_type}. Use: summary, risk_note, client_email")

    start_time = time.time()

    # Create a broad retrieval query tailored to the report type
    retrieval_queries = {
        "summary": "portfolio overview holdings allocation performance returns",
        "risk_note": "risk factors concentration exposure volatility compliance",
        "client_email": "client portfolio summary performance outlook recommendations",
    }

    # Embed the retrieval query
    query_embedding = embed_query(retrieval_queries[report_type])

    # Retrieve more chunks for reports (they need comprehensive context)
    chunks = retrieve_relevant_chunks(
        db, query_embedding, document_ids, top_k=settings.TOP_K_RESULTS * 2
    )

    if not chunks:
        return {
            "report_type": report_type,
            "content": "No documents available to generate this report. Please upload client documents first.",
            "sources_used": 0,
            "model_used": settings.OPENAI_MODEL,
        }

    # Build context from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i} — {chunk['filename']}, Page {chunk['page_number']}]\n"
            f"{chunk['content']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    # Fill the prompt template
    additional = f"\nAdditional Instructions: {additional_instructions}" if additional_instructions else ""
    prompt = REPORT_TEMPLATES[report_type].format(
        context=context,
        additional_instructions=additional,
    )

    # Call the LLM
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Generate the {report_type.replace('_', ' ')} report."},
        ],
        temperature=0.2,  # Slightly higher than Q&A for more natural report writing
        max_tokens=3000,
    )

    content = response.choices[0].message.content
    tokens_used = response.usage.total_tokens if response.usage else None
    response_time_ms = (time.time() - start_time) * 1000

    # Log for audit
    log_interaction(
        db=db,
        action_type=f"report_{report_type}",
        user_query=f"Generate {report_type} report",
        retrieved_chunk_ids=[str(c["chunk_id"]) for c in chunks],
        llm_prompt=prompt,
        llm_response=content,
        model_used=settings.OPENAI_MODEL,
        tokens_used=tokens_used,
        response_time_ms=response_time_ms,
    )

    return {
        "report_type": report_type,
        "content": content,
        "sources_used": len(chunks),
        "model_used": settings.OPENAI_MODEL,
    }
