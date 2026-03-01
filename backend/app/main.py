"""
main.py — FastAPI Application Entry Point

This module initializes the FastAPI application, configures middleware,
and registers all API route handlers. On startup, it ensures the database
tables and pgvector extension are created.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.database import init_db
from app.api import documents, chat, reports


# ──────────────────────────────────────────────
# Lifespan: runs on startup and shutdown
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: Initialize database tables and pgvector extension.
    Shutdown: (cleanup if needed in the future)
    """
    print("🚀 Starting AI Financial Advisor Assistant...")
    init_db()
    print("✅ Database initialized successfully")
    yield
    print("👋 Shutting down...")


# ──────────────────────────────────────────────
# Create FastAPI App
# ──────────────────────────────────────────────
app = FastAPI(
    title="AI Financial Advisor Assistant",
    description=(
        "A RAG-powered assistant that helps financial advisors answer client "
        "questions, summarize portfolios, and draft reports from indexed documents."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ──────────────────────────────────────────────
# CORS Middleware
# Allows the React frontend to communicate with the API.
# In production, restrict origins to your actual domain.
# ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Register API Routers
# Each router handles a specific domain of the application.
# ──────────────────────────────────────────────
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


# ──────────────────────────────────────────────
# Health Check Endpoint
# ──────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    """Returns service status. Useful for load balancers and monitoring."""
    return {"status": "healthy", "service": "ai-financial-advisor"}
