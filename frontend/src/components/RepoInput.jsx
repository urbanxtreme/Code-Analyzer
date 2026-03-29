import { useState } from 'react';
import { parseGitHubUrl } from '../utils/formatters';
import './RepoInput.css';

const EXAMPLES = [
  'facebook/react',
  'microsoft/vscode',
  'torvalds/linux',
  'vercel/next.js',
];

export default function RepoInput({ onAnalyze, disabled }) {
  const [url, setUrl] = useState('');
  const [validationError, setValidationError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setValidationError('');

    const trimmed = url.trim();
    if (!trimmed) {
      setValidationError('Please enter a GitHub repository URL');
      return;
    }

    // Accept both full URLs and owner/repo shorthand
    let fullUrl = trimmed;
    if (!trimmed.startsWith('http')) {
      fullUrl = `https://github.com/${trimmed}`;
    }

    const parsed = parseGitHubUrl(fullUrl);
    if (!parsed) {
      setValidationError('Invalid GitHub URL. Use format: https://github.com/owner/repo');
      return;
    }

    onAnalyze(fullUrl);
  };

  const handleExampleClick = (example) => {
    setUrl(`https://github.com/${example}`);
    setValidationError('');
  };

  return (
    <div className="repo-input-wrapper" id="repo-input">
      <form className="repo-input-form" onSubmit={handleSubmit}>
        <div className="repo-input-field-wrapper">
          <input
            type="text"
            className={`repo-input-field ${validationError ? 'input-error' : ''}`}
            placeholder="Enter a GitHub repository URL..."
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              if (validationError) setValidationError('');
            }}
            disabled={disabled}
            id="repo-url-input"
            autoComplete="off"
            spellCheck="false"
          />
          <span className="repo-input-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
              <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
            </svg>
          </span>
        </div>
        <button
          type="submit"
          className="repo-input-submit"
          disabled={disabled}
          id="analyze-button"
        >
          <span className="btn-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </span>
          Analyze
        </button>
      </form>

      {validationError && (
        <div className="repo-input-error-msg" role="alert">
          ⚠️ {validationError}
        </div>
      )}

      <p className="repo-input-hint">
        Paste a public GitHub URL or use shorthand like <code>owner/repo</code>
      </p>

      <div className="repo-input-examples">
        <span style={{ color: 'var(--text-muted)', fontSize: 'var(--fs-xs)' }}>Try:</span>
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            type="button"
            className="repo-input-example-btn"
            onClick={() => handleExampleClick(ex)}
            disabled={disabled}
          >
            {ex}
          </button>
        ))}
      </div>
    </div>
  );
}
