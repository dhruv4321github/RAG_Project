# 🏦 AI Financial Advisor Assistant with Secure RAG

A production-grade GenAI tool that helps financial advisors answer client questions, summarize portfolios, and draft reports using **Retrieval-Augmented Generation (RAG)** over securely indexed financial documents.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![React](https://img.shields.io/badge/React-18-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.1-orange)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-purple)

---

## 📋 Table of Contents

- [Demo](#demo)
- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [How the RAG Pipeline Works](#how-the-rag-pipeline-works)
- [Security & Audit Logging](#security--audit-logging)
- [Screenshots](#screenshots)
- [Future Enhancements](#future-enhancements)

---

## Demo
[Link](https://rag-project-ivory.vercel.app/)
May take some time to load

## Overview

Financial advisors deal with large volumes of client documents — portfolio statements, risk disclosures, investment policies, and regulatory filings. This tool allows advisors to:

1. **Upload client documents** (PDF, DOCX, TXT) which are chunked, embedded, and indexed into a vector database.
2. **Ask natural-language questions** about the uploaded documents and receive accurate, grounded answers via RAG.
3. **Generate reports** — portfolio summaries, risk notes, and draft client emails — all backed by retrieved document context.
4. **Audit every interaction** — all prompts, retrieved contexts, and LLM responses are logged for compliance.

### Workflow

```
Upload Docs → System Indexes & Embeds → Advisor Asks Questions → RAG Retrieves Context
→ LLM Generates Answer → Produces Summaries/Risk Notes/Emails → Logs Everything for Audit
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Document  │  │    Chat      │  │  Report/Audit    │  │
│  │ Upload    │  │  Interface   │  │    Panels        │  │
│  └─────┬────┘  └──────┬───────┘  └────────┬─────────┘  │
└────────┼───────────────┼──────────────────┼─────────────┘
         │               │                  │
         ▼               ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ /api/docs │  │  /api/chat   │  │  /api/reports    │  │
│  └─────┬────┘  └──────┬───────┘  └────────┬─────────┘  │
│        │               │                   │            │
│        ▼               ▼                   ▼            │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Document  │  │    RAG       │  │    Report        │  │
│  │ Processor │  │  Pipeline    │  │   Generator      │  │
│  └─────┬────┘  └──────┬───────┘  └────────┬─────────┘  │
│        │               │                   │            │
│        ▼               ▼                   ▼            │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Audit Logger (all interactions)     │    │
│  └─────────────────────┬───────────────────────────┘    │
└────────────────────────┼────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  PostgreSQL + pgvector                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  documents   │  │  embeddings  │  │  audit_logs  │  │
│  │  (metadata)  │  │  (vectors)   │  │  (prompts/   │  │
│  │              │  │              │  │   responses)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| **Backend** | Python 3.11, FastAPI                |
| **AI/LLM**  | LangChain, Ollama (Llama 3.1 / Mistral — free) or OpenAI (paid) |
| **Embeddings** | `nomic-embed-text` via Ollama (free) or OpenAI `text-embedding-3-small` |
| **Vector DB** | PostgreSQL + pgvector extension    |
| **Frontend** | React 18, CSS                      |
| **Infra**   | Docker, Docker Compose              |
| **Deployment** | AWS-ready (ECS/EC2 compatible)   |

---

## Project Structure

```
ai-financial-advisor-rag/
├── README.md                    # This file
├── docker-compose.yml           # Orchestrates all services
├── .env.example                 # Environment variable template
├── .gitignore
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── README.md                # Backend-specific documentation
│   └── app/
│       ├── main.py              # FastAPI application entry point
│       ├── config.py            # Environment & app configuration
│       ├── models/
│       │   ├── schemas.py       # Pydantic request/response models
│       │   └── database.py      # SQLAlchemy models & DB setup
│       ├── api/
│       │   ├── documents.py     # Document upload & management routes
│       │   ├── chat.py          # RAG chat/query routes
│       │   └── reports.py       # Report generation & audit routes
│       ├── services/
│       │   ├── document_processor.py  # PDF/DOCX parsing, chunking, embedding
│       │   ├── rag_pipeline.py        # Core RAG: retrieve + generate
│       │   ├── report_generator.py    # Summary, risk note, email generation
│       │   └── audit_logger.py        # Compliance logging service
│       └── utils/
│           └── security.py      # Input sanitization & validation
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── README.md                # Frontend-specific documentation
    ├── public/
    │   └── index.html
    └── src/
        ├── index.js
        ├── App.jsx              # Main app with routing
        ├── components/
        │   ├── ChatInterface.jsx    # Chat UI with message history
        │   ├── DocumentUpload.jsx   # Drag-and-drop document upload
        │   ├── ReportPanel.jsx      # Report generation UI
        │   └── AuditLog.jsx         # Audit trail viewer
        ├── services/
        │   └── api.js           # Axios API client
        └── styles/
            └── App.css          # Global styles
```

---

## Getting Started

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Ollama** installed ([ollama.com](https://ollama.com)) — *free, runs models locally*

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-financial-advisor-rag.git
cd ai-financial-advisor-rag
```

### 2. Pull Free LLM Models via Ollama

```bash
# Install Ollama from https://ollama.com, then:
ollama pull llama3.1          # 8B parameter LLM (free, ~4.7GB)
ollama pull nomic-embed-text  # Embedding model (free, ~274MB)
```

Other great free options: `mistral`, `gemma2`, `phi3`, `llama3.1:70b` (if you have a beefy GPU).

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

The default config uses OpenAI (paid). If you want Ollama (free) instead, edit `.env`. No API key needed!:
```env
LLM_PROVIDER=ollama
OPENAI_API_KEY=sk-your-key-here
```

### 4. Start All Services

```bash
docker-compose up --build
```

This starts three services:
- **PostgreSQL + pgvector** on port `5432`
- **FastAPI Backend** on port `8000`
- **React Frontend** on port `3000`

### 4. Access the Application

- **Frontend:** http://localhost:3000
- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc

---

## Configuration

All configuration is managed via environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | `ollama` (free, local) or `openai` (paid) | `openai` |
| `OLLAMA_MODEL` | Ollama model name | `llama3.1` |
| `OLLAMA_EMBEDDING_MODEL` | Ollama embedding model | `nomic-embed-text` |
| `OPENAI_API_KEY` | OpenAI key (only if provider=openai) | — |
| `OPENAI_MODEL` | OpenAI model (only if provider=openai) | `gpt-4.1-mini` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@db:5432/advisor_rag` |
| `CHUNK_SIZE` | Document chunk size (chars) | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks | `200` |
| `TOP_K_RESULTS` | Number of chunks to retrieve | `5` |
| `MAX_FILE_SIZE_MB` | Maximum upload file size | `50` |

---

## API Reference

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents/upload` | Upload and index a document |
| `GET` | `/api/documents/` | List all uploaded documents |
| `GET` | `/api/documents/{id}` | Get document metadata |
| `DELETE` | `/api/documents/{id}` | Delete document and its embeddings |

### Chat (RAG)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat/query` | Ask a question — returns RAG-grounded answer |
| `GET` | `/api/chat/history` | Get chat history for a session |

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/reports/summary` | Generate a portfolio summary |
| `POST` | `/api/reports/risk-note` | Generate a risk assessment note |
| `POST` | `/api/reports/client-email` | Draft a client email |
| `GET` | `/api/reports/audit-log` | View audit trail of all interactions |

---

## How the RAG Pipeline Works

The Retrieval-Augmented Generation pipeline is the core of this application. Here's what happens step-by-step:

### 1. Document Ingestion (`document_processor.py`)

```
Upload PDF/DOCX/TXT
        │
        ▼
  Parse raw text (PyPDF2 / python-docx)
        │
        ▼
  Split into chunks (LangChain RecursiveCharacterTextSplitter)
    - chunk_size: 1000 chars
    - chunk_overlap: 200 chars (preserves context at boundaries)
        │
        ▼
  Generate embeddings (OpenAI or Ollama nomic-embed-text)
    - Each chunk → vector (768-dim for Ollama, 1536-dim for OpenAI)
        │
        ▼
  Store in PostgreSQL/pgvector
    - Vector + chunk text + metadata (source doc, page, position)
```

### 2. Query Processing (`rag_pipeline.py`)

```
User asks: "What is the client's risk tolerance?"
        │
        ▼
  Embed the query → vector (same model used for documents)
        │
        ▼
  Similarity search in pgvector (cosine distance)
    - Returns top-K most relevant chunks
        │
        ▼
  Build prompt with retrieved context:
    ┌──────────────────────────────────────────────┐
    │ SYSTEM: You are a financial advisor assistant │
    │ CONTEXT: [chunk1] [chunk2] [chunk3]...       │
    │ QUESTION: What is the client's risk tolerance│
    │ INSTRUCTIONS: Answer only from context.       │
    │ If unsure, say "I don't have enough info."   │
    └──────────────────────────────────────────────┘
        │
        ▼
  LLM generates grounded response
        │
        ▼
  Log prompt + context + response to audit table
        │
        ▼
  Return answer + source references to frontend
```

### 3. Report Generation (`report_generator.py`)

Uses specialized prompt templates for each report type:

- **Portfolio Summary**: Synthesizes holdings, allocations, performance data
- **Risk Note**: Identifies risk factors, concentrations, regulatory concerns
- **Client Email**: Professional, compliant email drafts with proper disclaimers

---

## Security & Audit Logging

### Security Measures

- **Input Sanitization**: All user inputs are sanitized to prevent prompt injection attacks
- **File Validation**: Uploaded files are validated for type, size, and content
- **No Direct DB Access**: All database operations go through parameterized queries via SQLAlchemy
- **Environment Isolation**: Secrets are managed via environment variables, never hardcoded

### Audit Logging

Every interaction is logged to the `audit_logs` table:

```json
{
  "id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "action_type": "chat_query",
  "user_query": "What is the client's risk tolerance?",
  "retrieved_chunks": ["chunk_id_1", "chunk_id_2"],
  "llm_prompt": "System: You are a financial advisor...",
  "llm_response": "Based on the documents, the client has a moderate...",
  "model_used": "gpt-4.1-mini",
  "tokens_used": 1250,
  "response_time_ms": 2340
}
```

This ensures full traceability for **regulatory compliance** and **audit readiness**.

---

## Screenshots

> After running the application, you'll see:
> - A document upload panel for ingesting client files
> - A chat interface for asking questions about uploaded documents
> - A report generation panel for creating summaries, risk notes, and emails
> - An audit log viewer showing all recorded interactions

---

## Future Enhancements

- [ ] **Multi-tenancy**: Isolate data per advisor/team
- [ ] **LangGraph Workflows**: Multi-step agent reasoning with conditional branching
- [ ] **Streaming Responses**: Server-Sent Events for real-time LLM output
- [ ] **Role-Based Access Control**: Admin, advisor, and compliance officer roles
- [ ] **AWS Deployment**: Terraform scripts for ECS/RDS/S3 deployment
- [ ] **GPU Acceleration**: CUDA support for faster local inference with larger models
- [ ] **Document Versioning**: Track changes across document uploads
- [ ] **Export to PDF**: Generate downloadable compliance reports

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
