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

    LLM Provider Options:
      - "ollama"  → Free, local. Runs models like Llama 3, Mistral via Ollama.
      - "openai"  → Paid, cloud. Uses GPT-4, GPT-3.5, etc.

    When using Ollama:
      - Install Ollama: https://ollama.com
      - Pull a model:   ollama pull llama3.1
      - Pull embeddings: ollama pull nomic-embed-text
      - Ollama runs on http://localhost:11434 by default
    """

    # ── LLM Provider ──────────────────────────
    LLM_PROVIDER: str = "ollama"  # "ollama" (free) or "openai" (paid)

    # ── Ollama Settings (Free, Local) ─────────
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434/v1"  # Docker → host
    OLLAMA_MODEL: str = "llama3.1"              # or mistral, gemma2, phi3, etc.
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"
    OLLAMA_EMBEDDING_DIMENSIONS: int = 768      # nomic-embed-text outputs 768-dim

    # ── OpenAI Settings (Paid, Cloud) ─────────
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSIONS: int = 1536     # text-embedding-3-small outputs 1536-dim

    # ── Resolved Settings (computed from provider) ──
    @property
    def LLM_MODEL(self) -> str:
        return self.OLLAMA_MODEL if self.LLM_PROVIDER == "ollama" else self.OPENAI_MODEL

    @property
    def EMBEDDING_MODEL(self) -> str:
        return self.OLLAMA_EMBEDDING_MODEL if self.LLM_PROVIDER == "ollama" else self.OPENAI_EMBEDDING_MODEL

    @property
    def EMBEDDING_DIMENSIONS(self) -> int:
        return self.OLLAMA_EMBEDDING_DIMENSIONS if self.LLM_PROVIDER == "ollama" else self.OPENAI_EMBEDDING_DIMENSIONS

    @property
    def LLM_BASE_URL(self) -> str:
        return self.OLLAMA_BASE_URL if self.LLM_PROVIDER == "ollama" else self.OPENAI_BASE_URL

    @property
    def LLM_API_KEY(self) -> str:
        # Ollama doesn't need an API key, but the OpenAI client requires one
        return "ollama" if self.LLM_PROVIDER == "ollama" else self.OPENAI_API_KEY

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
