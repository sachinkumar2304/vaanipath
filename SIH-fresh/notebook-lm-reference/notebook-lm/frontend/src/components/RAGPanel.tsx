import React, { useState, useRef } from 'react';
import { Upload, Send, Loader, FileText } from 'lucide-react';
import axios from 'axios';
import './RAGPanel.css';

interface RAGPanelProps {
  theme: 'light' | 'dark';
  onDocumentUploaded: (documentId: string) => void;
  documentId: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const RAGPanel: React.FC<RAGPanelProps> = ({ theme, onDocumentUploaded, documentId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/documents/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      onDocumentUploaded(response.data.document_id);
      setUploadedFileName(file.name);
      setMessages([{
        role: 'assistant',
        content: `Document "${file.name}" uploaded successfully! I've processed ${response.data.chunks_count} chunks. Ask me anything about it!`
      }]);
    } catch (error) {
      console.error('Upload error:', error);
      setMessages([{
        role: 'assistant',
        content: 'Sorry, there was an error uploading the document. Please try again.'
      }]);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !documentId) return;

    const userMessage: Message = { role: 'user', content: inputMessage };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        message: inputMessage,
        document_id: documentId,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className={`rag-panel ${theme}`}>
      <div className="panel-header">
        <h2 className="panel-title">Document Chat</h2>
        <button
          className="upload-button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
        >
          {isUploading ? (
            <Loader className="spin" size={20} />
          ) : (
            <Upload size={20} />
          )}
          <span>{uploadedFileName || 'Upload PDF'}</span>
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileUpload}
          style={{ display: 'none' }}
        />
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <FileText size={64} />
            <p>Upload a PDF document to start chatting</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                {message.content}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <Loader className="spin" size={16} /> Thinking...
            </div>
          </div>
        )}
      </div>

      <div className="input-container">
        <input
          type="text"
          placeholder={documentId ? "Ask a question about your document..." : "Upload a document first..."}
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={!documentId || isLoading}
          className="message-input"
        />
        <button
          className="send-button"
          onClick={handleSendMessage}
          disabled={!documentId || !inputMessage.trim() || isLoading}
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};

export default RAGPanel;
