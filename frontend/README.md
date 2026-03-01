# Frontend — React Application

The React frontend provides an intuitive interface for financial advisors to interact with the RAG-powered AI assistant.

## Component Walkthrough

### `App.jsx` — Root Component

The main application shell. It manages:
- **Tab navigation** between the four main views (Documents, Chat, Reports, Audit)
- **Global document state** — fetches the document list and passes it down to child components that need it
- **Layout** — header, navigation, content area, footer

### `components/DocumentUpload.jsx` — File Upload

The document management interface where advisors upload client files:

- **Drag-and-drop zone**: Uses HTML5 drag events (`dragenter`, `dragover`, `dragleave`, `drop`) to detect when a file is being dragged over the upload area
- **File validation**: Client-side checks for file type (PDF, DOCX, TXT only) before sending to the server. The server performs its own validation too (defense in depth)
- **Upload state**: Shows a spinner while the backend processes the file through the full ingestion pipeline (parse → chunk → embed → store)
- **Document list**: Shows all uploaded documents with their status (`processing`, `ready`, `error`), file size, chunk count, and upload date
- **Delete**: Removes a document and all its indexed chunks from the database

### `components/ChatInterface.jsx` — RAG Chat

The primary interaction point for advisors:

- **Document scoping**: Optional chips at the top let advisors filter which documents to search. If none are selected, all documents are searched
- **Message history**: Maintains a local array of `{role, content, sources}` objects displayed as a conversation thread
- **Example queries**: When the chat is empty, shows clickable example questions to help new users get started
- **Source references**: Each AI response shows the retrieved document chunks that were used as context, including the document name and a relevance score (cosine similarity percentage)
- **Keyboard shortcut**: Enter to send, Shift+Enter for newline
- **Loading state**: Animated typing indicator while waiting for the RAG pipeline response

### `components/ReportPanel.jsx` — Report Generation

Generates three types of financial reports:

- **Report type cards**: Visual selection between Portfolio Summary, Risk Assessment, and Client Email
- **Additional instructions**: Optional textarea for advisors to provide extra context (e.g., "Focus on fixed income" or "Address the client as Mr. Smith")
- **Report display**: Renders the generated report with metadata (model used, number of source chunks)
- **Copy to clipboard**: One-click copy for pasting into other tools (email clients, Word docs, etc.)

### `components/AuditLog.jsx` — Compliance Viewer

Displays the full audit trail:

- **Expandable entries**: Click any entry to see the full query and response details
- **Metadata display**: Shows the action type, model used, token consumption, and response latency for each interaction
- **Refresh button**: Fetches the latest audit entries on demand
- **Compliance-ready**: This component exists specifically because financial regulations require full traceability of AI-generated content

### `services/api.js` — API Client

Centralized Axios client that all components use:

- **Base URL configuration**: Reads from `REACT_APP_API_URL` environment variable, defaults to `localhost:8000` for development
- **Endpoint functions**: Each API call is a named export function, making it easy to see all available API operations in one place
- **FormData handling**: The upload endpoint uses `multipart/form-data` content type for file uploads; all others use JSON

## Running Locally (Without Docker)

```bash
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
```

## Building for Production

```bash
npm run build
```

Creates an optimized production build in the `build/` directory, ready to be served by nginx or any static file server.
