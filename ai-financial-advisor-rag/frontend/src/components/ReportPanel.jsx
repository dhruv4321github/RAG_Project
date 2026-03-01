/**
 * ReportPanel.jsx — Report Generation Interface
 *
 * Allows advisors to generate three types of reports:
 *   1. Portfolio Summary
 *   2. Risk Assessment Note
 *   3. Client Email Draft
 *
 * Each report is generated using the RAG pipeline with specialized
 * prompt templates. Reports can be copied to clipboard for use in
 * other applications.
 */

import React, { useState } from 'react';
import { generateSummary, generateRiskNote, generateClientEmail } from '../services/api';

const REPORT_TYPES = [
  {
    id: 'summary',
    label: '📋 Portfolio Summary',
    description: 'Comprehensive overview of holdings, allocations, and performance',
    generator: generateSummary,
  },
  {
    id: 'risk_note',
    label: '⚠️ Risk Assessment',
    description: 'Identify concentration risks, market exposure, and compliance concerns',
    generator: generateRiskNote,
  },
  {
    id: 'client_email',
    label: '✉️ Client Email',
    description: 'Draft a professional, compliant client communication',
    generator: generateClientEmail,
  },
];

function ReportPanel({ documents }) {
  const [selectedType, setSelectedType] = useState('summary');
  const [instructions, setInstructions] = useState('');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const readyDocs = documents.filter((d) => d.status === 'ready');

  const handleGenerate = async () => {
    const reportConfig = REPORT_TYPES.find((r) => r.id === selectedType);
    if (!reportConfig) return;

    setLoading(true);
    setError(null);
    setReport(null);

    try {
      const res = await reportConfig.generator(
        null, // Use all documents
        instructions || null
      );
      setReport(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate report. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (report?.content) {
      navigator.clipboard.writeText(report.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="panel">
      <h2>Generate Reports</h2>
      <p className="panel-description">
        Generate AI-powered reports from your uploaded documents.
        All reports are based solely on document content and logged for compliance.
      </p>

      {readyDocs.length === 0 ? (
        <div className="empty-state">
          <p>Upload and index documents first before generating reports.</p>
        </div>
      ) : (
        <>
          {/* Report Type Selection */}
          <div className="report-types">
            {REPORT_TYPES.map((type) => (
              <button
                key={type.id}
                className={`report-type-card ${selectedType === type.id ? 'selected' : ''}`}
                onClick={() => setSelectedType(type.id)}
              >
                <h4>{type.label}</h4>
                <p>{type.description}</p>
              </button>
            ))}
          </div>

          {/* Additional Instructions */}
          <div className="instructions-input">
            <label>Additional instructions (optional):</label>
            <textarea
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              placeholder="e.g., Focus on fixed income allocation, address the client by name John..."
              rows={3}
            />
          </div>

          {/* Generate Button */}
          <button
            className="btn-generate"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? '⏳ Generating...' : '✨ Generate Report'}
          </button>

          {/* Error */}
          {error && <div className="error-message">{error}</div>}

          {/* Generated Report */}
          {report && (
            <div className="report-output">
              <div className="report-header">
                <h3>Generated Report</h3>
                <div className="report-meta">
                  <span>Model: {report.model_used}</span>
                  <span>Sources: {report.sources_used} chunks</span>
                  <button className="btn-copy" onClick={handleCopy}>
                    {copied ? '✅ Copied!' : '📋 Copy'}
                  </button>
                </div>
              </div>
              <div className="report-content">
                {report.content.split('\n').map((line, i) => (
                  <p key={i}>{line || <br />}</p>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default ReportPanel;
