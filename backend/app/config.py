"""
config.py — Application Configuration

Uses pydantic-settings to load and validate environment variables.
This is the single source of truth for all configurable parameters.
Values can be overridden via environment variables or a .env file.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Each field has a sensible default for development.
    """

    # ── OpenAI / LLM ──────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536  # Matches text-embedding-3-small output

    # ── Database ───────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/advisor_rag"

    # ── RAG Parameters ─────────────────────────
    CHUNK_SIZE: int = 1000       # Characters per chunk
    CHUNK_OVERLAP: int = 200     # Overlap between consecutive chunks
    TOP_K_RESULTS: int = 5       # Number of chunks to retrieve per query

    # ── File Upload ────────────────────────────
    MAX_FILE_SIZE_MB: int = 50
    UPLOAD_DIR: str = "/app/uploads"

    # ── Application ────────────────────────────
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance — import this throughout the app
settings = Settings()
