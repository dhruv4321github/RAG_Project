/**
 * DocumentUpload.jsx — Document Upload & Management
 *
 * Features:
 *   - Drag-and-drop file upload area
 *   - Click-to-browse file selection
 *   - Upload progress indication
 *   - Document list with status badges
 *   - Delete functionality
 *
 * Accepted file types: PDF, DOCX, TXT
 */

import React, { useState, useRef } from 'react';
import { uploadDocument, deleteDocument } from '../services/api';

function DocumentUpload({ documents, onRefresh }) {
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  // Handle file selection (from click or drop)
  const handleFiles = async (files) => {
    const file = files[0];
    if (!file) return;

    // Client-side validation
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const allowedExtensions = ['pdf', 'docx', 'txt'];
    const ext = file.name.split('.').pop().toLowerCase();

    if (!allowedExtensions.includes(ext)) {
      setError(`File type .${ext} is not supported. Please upload PDF, DOCX, or TXT files.`);
      return;
    }

    setError(null);
    setUploading(true);

    try {
      await uploadDocument(file);
      await onRefresh();
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  // Drag event handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  // Delete a document
  const handleDelete = async (id) => {
    if (!window.confirm('Delete this document and all its indexed data?')) return;
    try {
      await deleteDocument(id);
      await onRefresh();
    } catch (err) {
      setError('Failed to delete document.');
    }
  };

  // Format file size for display
  const formatSize = (bytes) => {
    if (!bytes) return 'N/A';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // Status badge color
  const statusClass = (status) => {
    switch (status) {
      case 'ready': return 'status-ready';
      case 'processing': return 'status-processing';
      case 'error': return 'status-error';
      default: return '';
    }
  };

  return (
    <div className="panel">
      <h2>Upload Documents</h2>
      <p className="panel-description">
        Upload client documents (PDF, DOCX, TXT) to index them for AI-powered search and analysis.
      </p>

      {/* Drag & Drop Zone */}
      <div
        className={`upload-zone ${dragActive ? 'drag-active' : ''} ${uploading ? 'uploading' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={(e) => handleFiles(e.target.files)}
          style={{ display: 'none' }}
        />
        {uploading ? (
          <div className="upload-spinner">
            <div className="spinner"></div>
            <p>Processing document... This may take a moment.</p>
          </div>
        ) : (
          <>
            <span className="upload-icon">📁</span>
            <p><strong>Drag & drop</strong> a file here, or <strong>click to browse</strong></p>
            <p className="upload-hint">Supports PDF, DOCX, TXT — Max 50 MB</p>
          </>
        )}
      </div>

      {/* Error Message */}
      {error && <div className="error-message">{error}</div>}

      {/* Document List */}
      <h3>Uploaded Documents ({documents.length})</h3>
      {documents.length === 0 ? (
        <p className="empty-state">No documents uploaded yet. Upload a file to get started.</p>
      ) : (
        <div className="document-list">
          {documents.map((doc) => (
            <div key={doc.id} className="document-card">
              <div className="doc-info">
                <span className="doc-icon">
                  {doc.file_type === 'pdf' ? '📕' : doc.file_type === 'docx' ? '📘' : '📝'}
                </span>
                <div>
                  <h4>{doc.filename}</h4>
                  <p className="doc-meta">
                    {formatSize(doc.file_size_bytes)} · {doc.chunk_count} chunks ·{' '}
                    {new Date(doc.uploaded_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="doc-actions">
                <span className={`status-badge ${statusClass(doc.status)}`}>
                  {doc.status}
                </span>
                <button
                  className="btn-delete"
                  onClick={() => handleDelete(doc.id)}
                  title="Delete document"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default DocumentUpload;
