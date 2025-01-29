import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './styles.css';

const App = () => {
    const [repoUrl, setRepoUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [results, setResults] = useState(null);
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState('');

    const handleAnalyze = async () => {
        setLoading(true);
        setError(null);
        setResults(null);
        setProgress(0);
        setStatus('');

        try {
            const isProduction = process.env.NODE_ENV === "production";
            const ws = new WebSocket(
                isProduction
                    ? `${window.location.origin.replace(/^http/, "ws")}/ws/progress`
                    : "ws://localhost:8000/ws/progress"
            );

            ws.onopen = () => {
                ws.send(repoUrl);
            };
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.error) {
                    setError(data.error);
                    setLoading(false);
                } else if (data.progress !== undefined) {
                    setProgress(parseFloat(data.progress.toFixed(2)));
                } else if (data.results) {
                    setResults({ results: data.results });
                    setLoading(false);
                    const isMalicious = data.results.includes('[MALICIOUS]');
                    setStatus(isMalicious ? 'MALICIOUS REPOSITORY' : 'SECURE REPOSITORY');
                }
            };
            ws.onclose = () => {
                setLoading(false);
            };
        } catch (err) {
            setError('An error occurred while analyzing the repository: ' + err);
            setLoading(false);
        }
    };

    return (
        <div className="app-container">
            <div className="header">
                <img src="/images/icon.png" alt="Logo" className="logo" />
                <h1>Repomancer</h1>
            </div>
            <div className="description">
                <p>Scans GitHub repositories recursively for potential malicious code using AI and provides a detailed analysis.</p>
            </div>
            <div className="form-container">
                <input
                    type="text"
                    placeholder="Enter GitHub repository URL"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                />
                <button onClick={handleAnalyze} disabled={loading || !repoUrl}>
                    {loading ? 'Analyzing...' : 'Analyze'}
                </button>
            </div>

            {loading && <p className="processing">Processing: {progress}%</p>} 
            {error && <p className="error-message">{error}</p>}

            {status && (
                <div className={`status-message ${status === 'MALICIOUS REPOSITORY' ? 'malicious' : 'safe'}`}>
                    {status}
                </div>
            )}
            {results && results.results && (
                <div className="results-container p-4 bg-white shadow-lg rounded-xl">
                    <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
                    <div className="results-content text-xl font-semibold text-gray-800 mb-4">
                        <ReactMarkdown
                            children={results.results.replace('[MALICIOUS]', '').replace('[SAFE]', '')}
                            remarkPlugins={[remarkGfm]}
                            className="markdown-content"
                        />
                    </div>
                </div>
            )}
        </div>
    );
    
};

export default App;