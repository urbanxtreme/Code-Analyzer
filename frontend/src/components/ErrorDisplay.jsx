import './ErrorDisplay.css';

export default function ErrorDisplay({ message, onRetry, onBack }) {
  return (
    <div className="error-display" id="error-display">
      <div className="error-icon">💥</div>
      <h2 className="error-title">Analysis Failed</h2>
      <p className="error-message">
        {message || 'Something went wrong while analyzing the repository. Please check the URL and try again.'}
      </p>
      <div className="error-actions">
        <button className="error-retry-btn" onClick={onRetry} id="error-retry-btn">
          🔄 Try Again
        </button>
        <button className="error-back-btn" onClick={onBack} id="error-back-btn">
          ← Go Back
        </button>
      </div>
    </div>
  );
}
