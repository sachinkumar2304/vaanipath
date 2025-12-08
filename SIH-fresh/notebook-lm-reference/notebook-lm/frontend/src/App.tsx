import React, { useState } from 'react';
import './App.css';
import RAGPanel from './components/RAGPanel';
import PodcastPanel from './components/PodcastPanel';
import { Moon, Sun } from 'lucide-react';

function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [documentId, setDocumentId] = useState<string>('');

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <div className={`app ${theme}`}>
      <header className="app-header">
        <h1 className="app-title">NotebookLM</h1>
        <button className="theme-toggle" onClick={toggleTheme}>
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </button>
      </header>

      <div className="main-container">
        <div className="panel-container">
          <RAGPanel
            theme={theme}
            onDocumentUploaded={setDocumentId}
            documentId={documentId}
          />
        </div>
        <div className="panel-container">
          <PodcastPanel
            theme={theme}
            documentId={documentId}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
