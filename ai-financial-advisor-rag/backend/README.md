# Backend — FastAPI + LangChain + pgvector

This is the backend service for the AI Financial Advisor Assistant. It handles document ingestion, RAG-based querying, report generation, and audit logging.

## Code Walkthrough

### `app/main.py` — Application Entry Point

The FastAPI app is initialized here. It:
- Creates database tables on startup using SQLAlchemy
- Registers CORS middleware so the React frontend can communicate with it
- Mounts the three API routers: `documents`, `chat`, and `reports`

### `app/config.py` — Configuration

Uses `pydantic-settings` to load environment variables with type validation and defaults. This is the single source of truth for all configurable values (model names, chunk sizes, DB URL, etc.).

### `app/models/database.py` — Database Models

Defines three SQLAlchemy models mapping to PostgreSQL tables:

- **`Document`**: Stores metadata about each uploaded file (name, type, upload time, chunk count).
- **`DocumentChunk`**: Stores individual text chunks and their vector embeddings. The `embedding` column uses pgvector's `Vector(1536)` type for efficient similarity search.
- **`AuditLog`**: Records every interaction — the user's query, which chunks were retrieved, what prompt was sent to the LLM, and the generated response.

The `init_db()` function creates the pgvector extension and all tables on first run.

### `app/models/schemas.py` — Pydantic Schemas

Request and response models for the API. Using Pydantic ensures all inputs are validated before reaching business logic. Key schemas:
- `ChatRequest` / `ChatResponse` — for RAG queries
- `ReportRequest` / `ReportResponse` — for report generation
- `DocumentResponse` — metadata returned after upload

### `app/services/document_processor.py` — Document Ingestion

This is where uploaded files are turned into searchable vectors:

1. **Parse**: Extracts raw text from PDFs (PyPDF2), DOCX (python-docx), or plain text files
2. **Chunk**: Uses LangChain's `RecursiveCharacterTextSplitter` to break text into overlapping chunks. Overlap ensures that information at chunk boundaries isn't lost.
3. **Embed**: Sends each chunk to OpenAI's embedding API, returning a 1536-dimensional vector
4. **Store**: Inserts the chunk text, embedding vector, and metadata into PostgreSQL via pgvector

### `app/services/rag_pipeline.py` — Core RAG Logic

The heart of the application. When a user asks a question:

1. **Embed the query**: The question is converted to a vector using the same embedding model
2. **Retrieve**: pgvector performs a cosine similarity search, returning the top-K most relevant chunks
3. **Build prompt**: A structured prompt is assembled with:
   - A system message defining the assistant's role and constraints
   - The retrieved context chunks
   - The user's question
   - Instructions to only answer from the provided context
4. **Generate**: The prompt is sent to the LLM (GPT-4 by default)
5. **Log**: The entire interaction is recorded via the audit logger
6. **Return**: The answer and source references are sent back to the client

### `app/services/report_generator.py` — Report Generation

Uses specialized prompt templates to produce three types of financial documents:
- **Portfolio Summary**: Synthesizes document content into a structured overview
- **Risk Note**: Identifies and articulates risk factors found in the documents
- **Client Email**: Drafts professional, compliance-aware emails

Each report type retrieves relevant context via the RAG pipeline before generating.

### `app/services/audit_logger.py` — Compliance Logging

Every LLM interaction is logged with:
- Timestamp, action type, user query
- Which document chunks were retrieved (by ID)
- The full prompt sent to the LLM
- The LLM's response
- Token usage and response time

This creates a complete audit trail suitable for financial regulatory compliance.

### `app/utils/security.py` — Input Validation

Handles security concerns:
- **File validation**: Checks file extensions and MIME types against an allowlist
- **Input sanitization**: Strips potentially dangerous characters and patterns from user input to guard against prompt injection
- **Size limits**: Enforces maximum file upload sizes

### `app/api/` — Route Handlers

Thin API layer that validates inputs via Pydantic schemas, calls the appropriate service, and returns structured responses. Follows FastAPI best practices with dependency injection, proper HTTP status codes, and automatic OpenAPI documentation.

## Running Locally (Without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/advisor_rag
export OPENAI_API_KEY=sk-your-key

# Run the server
uvicorn app.main:app --reload --port 8000
```

Note: You'll need a local PostgreSQL instance with the pgvector extension installed.
