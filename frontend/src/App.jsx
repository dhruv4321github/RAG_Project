/**
 * App.jsx — Main Application Component
 *
 * Provides tab-based navigation between the four main features:
 *   1. Document Upload — manage uploaded files
 *   2. Chat — ask questions about documents (RAG)
 *   3. Reports — generate summaries, risk notes, emails
 *   4. Audit Log — view compliance trail
 */

import React, { useState, useEffect } from 'react';
import DocumentUpload from './components/DocumentUpload';
import ChatInterface from './components/ChatInterface';
import ReportPanel from './components/ReportPanel';
import AuditLog from './components/AuditLog';
import { getDocuments, pingHealth } from './services/api';

const TABS = [
  { id: 'documents', label: '📄 Documents', icon: '📄' },
  { id: 'chat', label: '💬 Chat', icon: '💬' },
  { id: 'reports', label: '📊 Reports', icon: '📊' },
  { id: 'audit', label: '🔍 Audit Log', icon: '🔍' },
];

function App() {
  const [activeTab, setActiveTab] = useState('documents');
  const [documents, setDocuments] = useState([]);
  const [backendReady, setBackendReady] = useState(false);

  const refreshDocuments = async () => {
    try {
      const res = await getDocuments();
      setDocuments(res.data);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    }
  };

  // On first load the backend may be cold-starting (Render's free tier spins
  // down after inactivity and takes ~30–60s to wake). Poll /health until it
  // responds so we can show a "please wait" banner instead of a broken UI.
  useEffect(() => {
    let cancelled = false;

    const waitForBackend = async () => {
      while (!cancelled) {
        try {
          await pingHealth();
          if (!cancelled) setBackendReady(true);
          return;
        } catch {
          // Still waking up — wait a few seconds and retry.
          await new Promise((resolve) => setTimeout(resolve, 3000));
        }
      }
    };

    waitForBackend();
    return () => {
      cancelled = true;
    };
  }, []);

  // Fetch documents once the backend is awake, and whenever the tab changes.
  useEffect(() => {
    if (backendReady) refreshDocuments();
  }, [activeTab, backendReady]);

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>🏦 AI Financial Advisor Assistant</h1>
          <p>Secure RAG-powered document intelligence for financial advisors</p>
        </div>
      </header>

      {/* Cold-start notice: shown until the backend responds to /health */}
      {!backendReady && (
        <div className="wakeup-banner" role="status" aria-live="polite">
          <div className="spinner" />
          <div>
            <strong>Waking up the server…</strong>
            <span>
              {' '}This can take 1–2 minutes on the first visit since the
              backend goes to sleep when idle. Hang tight — the app will load
              automatically once it's ready.
            </span>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <nav className="tab-nav">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Tab Content */}
      <main className="main-content">
        {activeTab === 'documents' && (
          <DocumentUpload
            documents={documents}
            onRefresh={refreshDocuments}
          />
        )}
        {activeTab === 'chat' && (
          <ChatInterface documents={documents} />
        )}
        {activeTab === 'reports' && (
          <ReportPanel documents={documents} />
        )}
        {activeTab === 'audit' && (
          <AuditLog />
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>AI Financial Advisor Assistant — All interactions are logged for compliance</p>
      </footer>
    </div>
  );
}

export default App;
