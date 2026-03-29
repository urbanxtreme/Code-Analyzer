import RepoInput from '../components/RepoInput';
import './HomePage.css';

export default function HomePage({ onAnalyze, loading }) {
  return (
    <div className="home-page" id="home-page">
      {/* Hero */}
      <section className="hero">
        <div className="hero-badge">
          <span className="hero-badge-dot"></span>
          AI-Powered Analysis
        </div>

        <h1 className="hero-title" id="hero-title">
          Decode Any GitHub
          <br />
          Repository with <span className="highlight">AI Intelligence</span>
        </h1>

        <p className="hero-description">
          Paste a public GitHub repository URL and let our AI deeply analyze contributor behavior,
          code quality, and team dynamics — generating actionable intelligence in seconds.
        </p>

        <RepoInput onAnalyze={onAnalyze} disabled={loading} />
      </section>

      {/* Stats */}
      <div className="stats-bar">
        <div className="stat-item">
          <div className="stat-value purple">6+</div>
          <div className="stat-label">Analysis Dimensions</div>
        </div>
        <div className="stat-item">
          <div className="stat-value cyan">AI</div>
          <div className="stat-label">Powered Insights</div>
        </div>
        <div className="stat-item">
          <div className="stat-value pink">100%</div>
          <div className="stat-label">Free & Local</div>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="features stagger-children">
        <div className="feature-card">
          <div className="feature-icon purple">👥</div>
          <div className="feature-title">Contributor Intelligence</div>
          <div className="feature-desc">
            Deep-dive into each contributor's commit patterns, code quality, and activity levels
            with personality-style labeling.
          </div>
        </div>

        <div className="feature-card">
          <div className="feature-icon cyan">🤖</div>
          <div className="feature-title">AI-Powered Insights</div>
          <div className="feature-desc">
            Local LLM explains the project in simple terms, describes team behavior, and highlights
            strengths, risks, and recommendations.
          </div>
        </div>

        <div className="feature-card">
          <div className="feature-icon pink">📊</div>
          <div className="feature-title">Pattern Detection</div>
          <div className="feature-desc">
            Visualize when contributors work, detect burst vs. steady patterns, and estimate
            AI-generated code likelihood.
          </div>
        </div>
      </div>
    </div>
  );
}
