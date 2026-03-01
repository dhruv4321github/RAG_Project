/**
 * api.js — Axios API Client
 *
 * Centralized API client that all components use to communicate
 * with the FastAPI backend. Using a single client ensures consistent
 * base URL configuration and error handling.
 */

import axios from 'axios';

// Base URL defaults to localhost for development.
// In Docker, the REACT_APP_API_URL env var points to the backend container.
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Document Endpoints ─────────────────────────

/** Upload a document file (PDF, DOCX, TXT) */
export const uploadDocument = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

/** Get list of all uploaded documents */
export const getDocuments = () => api.get('/api/documents/');

/** Delete a document by ID */
export const deleteDocument = (id) => api.delete(`/api/documents/${id}`);

// ── Chat Endpoints ─────────────────────────────

/** Send a RAG query and get a grounded answer */
export const sendQuery = (query, documentIds = null) =>
  api.post('/api/chat/query', {
    query,
    document_ids: documentIds,
  });

/** Get recent chat history */
export const getChatHistory = (limit = 20) =>
  api.get(`/api/chat/history?limit=${limit}`);

// ── Report Endpoints ───────────────────────────

/** Generate a portfolio summary */
export const generateSummary = (documentIds = null, instructions = null) =>
  api.post('/api/reports/summary', {
    report_type: 'summary',
    document_ids: documentIds,
    additional_instructions: instructions,
  });

/** Generate a risk assessment note */
export const generateRiskNote = (documentIds = null, instructions = null) =>
  api.post('/api/reports/risk-note', {
    report_type: 'risk_note',
    document_ids: documentIds,
    additional_instructions: instructions,
  });

/** Generate a client email draft */
export const generateClientEmail = (documentIds = null, instructions = null) =>
  api.post('/api/reports/client-email', {
    report_type: 'client_email',
    document_ids: documentIds,
    additional_instructions: instructions,
  });

/** Get the full audit log */
export const getAuditLog = (limit = 50) =>
  api.get(`/api/reports/audit-log?limit=${limit}`);

export default api;
