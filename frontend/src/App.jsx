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
import { getDocuments } from './services/api';

const TABS = [
  { id: 'documents', label: '📄 Documents', icon: '📄' },
  { id: 'chat', label: '💬 Chat', icon: '💬' },
  { id: 'reports', label: '📊 Reports', icon: '📊' },
  { id: 'audit', label: '🔍 Audit Log', icon: '🔍' },
];

function App() {
  const [activeTab, setActiveTab] = useState('documents');
  const [documents, setDocuments] = useState([]);

  // Fetch documents on mount and when tab changes
  const refreshDocuments = async () => {
    try {
      const res = await getDocuments();
      setDocuments(res.data);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    }
  };

  useEffect(() => {
    refreshDocuments();
  }, [activeTab]);

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>🏦 AI Financial Advisor Assistant</h1>
          <p>Secure RAG-powered document intelligence for financial advisors</p>
        </div>
      </header>

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
