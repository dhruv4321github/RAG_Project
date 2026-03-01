/**
 * AuditLog.jsx — Audit Trail Viewer
 *
 * Displays a compliance-ready log of all LLM interactions.
 * Each entry shows the action type, query, response preview,
 * model used, token consumption, and response time.
 *
 * This is essential for financial regulatory compliance — every
 * AI-generated answer must be traceable and reviewable.
 */

import React, { useState, useEffect } from 'react';
import { getAuditLog } from '../services/api';

function AuditLog() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await getAuditLog(100);
      setLogs(res.data);
    } catch (err) {
      setError('Failed to load audit logs.');
    } finally {
      setLoading(false);
    }
  };

  // Format action type for display
  const formatAction = (type) => {
    const labels = {
      chat_query: '💬 Chat Query',
      report_summary: '📋 Summary Report',
      report_risk_note: '⚠️ Risk Note',
      report_client_email: '✉️ Client Email',
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <div className="panel">
        <h2>Audit Log</h2>
        <div className="loading-state">Loading audit trail...</div>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>Audit Log</h2>
      <p className="panel-description">
        Complete record of all AI interactions. Every query, retrieved context,
        and generated response is logged for regulatory compliance.
      </p>

      <button className="btn-refresh" onClick={fetchLogs}>
        🔄 Refresh
      </button>

      {error && <div className="error-message">{error}</div>}

      {logs.length === 0 ? (
        <p className="empty-state">No interactions logged yet.</p>
      ) : (
        <div className="audit-list">
          {logs.map((log) => (
            <div
              key={log.id}
              className={`audit-entry ${expandedId === log.id ? 'expanded' : ''}`}
            >
              <div
                className="audit-summary"
                onClick={() => setExpandedId(expandedId === log.id ? null : log.id)}
              >
                <div className="audit-left">
                  <span className="audit-action">{formatAction(log.action_type)}</span>
                  <span className="audit-query">
                    {log.user_query
                      ? log.user_query.length > 80
                        ? log.user_query.substring(0, 80) + '...'
                        : log.user_query
                      : 'N/A'}
                  </span>
                </div>
                <div className="audit-right">
                  <span className="audit-model">{log.model_used}</span>
                  {log.tokens_used && (
                    <span className="audit-tokens">{log.tokens_used} tokens</span>
                  )}
                  {log.response_time_ms && (
                    <span className="audit-time">{log.response_time_ms.toFixed(0)}ms</span>
                  )}
                  <span className="audit-date">
                    {new Date(log.timestamp).toLocaleString()}
                  </span>
                  <span className="expand-icon">
                    {expandedId === log.id ? '▼' : '▶'}
                  </span>
                </div>
              </div>

              {/* Expanded Details */}
              {expandedId === log.id && (
                <div className="audit-details">
                  <div className="detail-section">
                    <h4>Query</h4>
                    <p>{log.user_query || 'N/A'}</p>
                  </div>
                  <div className="detail-section">
                    <h4>Response</h4>
                    <p>{log.llm_response || 'N/A'}</p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AuditLog;
