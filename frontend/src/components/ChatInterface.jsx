/**
 * ChatInterface.jsx — RAG Chat Interface
 *
 * The main interaction point for financial advisors. Features:
 *   - Message input with send button
 *   - Chat message history (user + AI messages)
 *   - Source references shown under each AI response
 *   - Loading state with animated indicator
 *   - Optional document scope filtering
 */

import React, { useState, useRef, useEffect } from 'react';
import { sendQuery } from '../services/api';

function ChatInterface({ documents }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedDocs, setSelectedDocs] = useState([]);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send a query to the RAG pipeline
  const handleSend = async () => {
    const query = input.trim();
    if (!query || loading) return;

    // Add user message to chat
    const userMessage = { role: 'user', content: query, timestamp: new Date() };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const docIds = selectedDocs.length > 0 ? selectedDocs : null;
      const res = await sendQuery(query, docIds);
      const data = res.data;

      // Add AI response to chat
      const aiMessage = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        model: data.model_used,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, an error occurred while processing your question. Please try again.',
        error: true,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // Handle Enter key
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Toggle document selection for scoped queries
  const toggleDoc = (id) => {
    setSelectedDocs((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    );
  };

  const readyDocs = documents.filter((d) => d.status === 'ready');

  return (
    <div className="panel chat-panel">
      <h2>Ask Questions</h2>
      <p className="panel-description">
        Ask questions about your uploaded documents. The AI retrieves relevant context
        and provides grounded answers with source references.
      </p>

      {/* Document Scope Filter */}
      {readyDocs.length > 0 && (
        <div className="doc-filter">
          <label>Search scope (optional — select specific documents):</label>
          <div className="doc-chips">
            {readyDocs.map((doc) => (
              <button
                key={doc.id}
                className={`doc-chip ${selectedDocs.includes(doc.id) ? 'selected' : ''}`}
                onClick={() => toggleDoc(doc.id)}
              >
                {doc.filename}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Chat Messages */}
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-chat">
            <span className="chat-icon">💬</span>
            <p>Ask a question about your uploaded documents</p>
            <div className="example-queries">
              <p><strong>Example questions:</strong></p>
              <button onClick={() => setInput('What is the client\'s current asset allocation?')}>
                "What is the client's current asset allocation?"
              </button>
              <button onClick={() => setInput('Are there any concentration risks in the portfolio?')}>
                "Are there any concentration risks in the portfolio?"
              </button>
              <button onClick={() => setInput('What is the client\'s stated risk tolerance?')}>
                "What is the client's stated risk tolerance?"
              </button>
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="message-header">
              <span className="message-role">
                {msg.role === 'user' ? '👤 You' : '🤖 Advisor AI'}
              </span>
              <span className="message-time">
                {msg.timestamp.toLocaleTimeString()}
              </span>
            </div>
            <div className={`message-content ${msg.error ? 'error' : ''}`}>
              {msg.content}
            </div>

            {/* Source references for AI messages */}
            {msg.sources && msg.sources.length > 0 && (
              <div className="sources">
                <p className="sources-label">📎 Sources:</p>
                {msg.sources.map((src, j) => (
                  <div key={j} className="source-card">
                    <div className="source-header">
                      <strong>{src.document_name}</strong>
                      <span className="relevance">
                        {(src.relevance_score * 100).toFixed(1)}% match
                      </span>
                    </div>
                    <p className="source-preview">{src.content_preview}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="message assistant">
            <div className="message-header">
              <span className="message-role">🤖 Advisor AI</span>
            </div>
            <div className="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="chat-input-area">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your documents..."
          rows={2}
          disabled={loading}
        />
        <button
          className="btn-send"
          onClick={handleSend}
          disabled={!input.trim() || loading}
        >
          {loading ? '⏳' : '➤'}
        </button>
      </div>
    </div>
  );
}

export default ChatInterface;
