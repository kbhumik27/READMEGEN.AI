import React, { useState, useEffect, useRef } from 'react';
import { FaSun, FaMoon, FaArrowDown } from 'react-icons/fa';
import './App.css';

const API_URL = 'http://localhost:8000'; 

export default function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState('Idle');
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const intervalRef = useRef(null);
  const generatorRef = useRef(null);
  
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);
  
  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  const scrollToGenerator = () => {
    generatorRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleDownload = () => {
    const blob = new Blob([result], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'README.md';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult('');
    setTaskId(null);
    setIsLoading(true);
    setStatus('Submitting job...');

    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl }),
      });
      if (!response.ok) throw new Error('Failed to start job.');
      const data = await response.json();
      setTaskId(data.task_id);
      setStatus('Job submitted. Waiting for progress...');
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
      setStatus('Idle');
    }
  };

  const checkStatus = async () => {
    if (!taskId) return;
    try {
      const response = await fetch(`${API_URL}/status/${taskId}`);
      const data = await response.json();
      setStatus(`Job Status: ${data.status}`);
      if (data.status === 'SUCCESS') {
        setResult(data.result);
        setIsLoading(false);
        clearInterval(intervalRef.current);
      } else if (data.status === 'FAILURE') {
        setError('Job failed. Check logs or result.');
        setResult(data.result); 
        setIsLoading(false);
        clearInterval(intervalRef.current);
      }
    } catch (err) {
      setError('Failed to fetch status.');
      setIsLoading(false);
      clearInterval(intervalRef.current);
    }
  };

  useEffect(() => {
    if (taskId) {
      intervalRef.current = setInterval(checkStatus, 3000);
    }
    return () => {
        if(intervalRef.current) {
            clearInterval(intervalRef.current);
        }
    };
  }, [taskId]);

  return (
    <div className="App">
      <button onClick={toggleTheme} className="theme-toggle-btn">
        {theme === 'light' ? <FaMoon /> : <FaSun />}
      </button>

      <div className="hero-section">
        <div className="hero-title-container">
          <h1 className="hero-title">:\\:README GEN. AI://:</h1>
        </div>
        <p className="hero-subtitle">
          AI-powered generation of comprehensive, context-aware README files for your GitHub repositories.
        </p>
        <button onClick={scrollToGenerator} className="hero-cta-btn">
          Initiate Generation <FaArrowDown style={{ marginLeft: '10px', verticalAlign: 'middle' }} />
        </button>
      </div>

      <div id="generator" ref={generatorRef}>
        <div className="generator-container"> 
          <h2>[ Generation Module ]</h2>
          <p>> Input repository URL below.</p>
          <form onSubmit={handleSubmit} className="form-container">
            <input
              type="url"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/user/repository"
              required
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Processing...' : 'Generate'}
            </button>
          </form>

          {taskId && (
            <div className="status-container">
              <h3>[ System Log ]</h3>
              <p className="status-text">{status}</p>
              {error && <p className="error-text">Error: {error}</p>}
            </div>
          )}

          {result && (
            <div className="result-container">
              <div className="result-header">
                <h3>[ Output File ]</h3>
                {!result.startsWith("TASK FAILED:") && (
                  <button onClick={handleDownload} className="download-btn">
                    Download README.md
                  </button>
                )}
              </div>
              <textarea readOnly value={result}></textarea>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}