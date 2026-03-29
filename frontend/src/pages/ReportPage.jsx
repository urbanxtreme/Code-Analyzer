import React from 'react';
import { formatNumber, formatDate } from '../utils/formatters';
import OverviewSection from '../sections/OverviewSection';
import ContributorSection from '../sections/ContributorSection';
import InsightsSection from '../sections/InsightsSection';
import PatternsSection from '../sections/PatternsSection';
import RecommendationsSection from '../sections/RecommendationsSection';
import CompositionSection from '../sections/CompositionSection';
import './ReportPage.css';

// Language colors (GitHub-style)
const LANG_COLORS = {
  JavaScript: '#f1e05a',
  TypeScript: '#3178c6',
  Python: '#3572A5',
  CSS: '#563d7c',
  HTML: '#e34c26',
  'C++': '#f34b7d',
  Java: '#b07219',
  Go: '#00ADD8',
  Rust: '#dea584',
  Ruby: '#701516',
  Swift: '#F05138',
  Kotlin: '#A97BFF',
  Shell: '#89e051',
};

function getLangColor(lang) {
  return LANG_COLORS[lang] || '#8b5cf6';
}

export default function ReportPage({ report, onReset }) {
  const { repository, ai_summary, contributors, insights, recommendations, patterns, structure } = report;

  const healthClass = repository.health_score > 80 ? 'excellent' : repository.health_score > 60 ? 'good' : 'fair';

  return (
    <div className="report-page" id="report-page">
      <div className="container">
        {/* Report Header */}
        <div className="report-header">
          <div className="report-header-left">
            <h1 className="report-repo-name">
              <a href={repository.url} target="_blank" rel="noopener noreferrer">
                {repository.full_name}
              </a>
              <span className="external-icon">↗</span>
            </h1>
            <p className="report-repo-desc">{repository.description}</p>
            
            {repository.topics && repository.topics.length > 0 && (
              <div className="report-topics">
                {repository.topics.map(topic => (
                  <span key={topic} className="topic-chip">{topic}</span>
                ))}
              </div>
            )}
          </div>

          <div className="report-header-right">
            <button className="report-back-btn" onClick={onReset} id="report-back-btn">
              ← New Analysis
            </button>
            <div className={`report-health-badge health-${healthClass}`}>
              <span className="dot"></span>
              {healthClass.toUpperCase()} HEALTH
            </div>
            {repository.license && (
              <div className="license-badge">
                <span className="icon">⚖️</span>
                {repository.license}
              </div>
            )}
          </div>
        </div>

        {/* Analysis Pulse Stats */}
        <div className="analysis-pulse">
          <div className="pulse-item">
            <span className="pulse-label">Intelligence Score</span>
            <div className="pulse-value-container">
              <span className="pulse-number">{repository.health_score}</span>
              <div className="pulse-progress-bg">
                <div className="pulse-progress-fill" style={{ width: `${repository.health_score}%` }}></div>
              </div>
            </div>
          </div>
          <div className="pulse-item">
            <span className="pulse-label">Last Activity</span>
            <span className="pulse-value">{repository.last_commit_days_ago === 0 ? 'Today' : `${repository.last_commit_days_ago}d ago`}</span>
          </div>
          <div className="pulse-item">
            <span className="pulse-label">Issue Momentum</span>
            <span className="pulse-value">{(repository.open_issues_to_stars_ratio * 100).toFixed(1)}% Ratio</span>
          </div>
          <div className="pulse-item">
            <span className="pulse-label">Project Clarity</span>
            <span className={`pulse-value status-${structure.documentation_status}`}>
              {structure.documentation_status.toUpperCase()}
            </span>
          </div>
        </div>

        <div className="repo-stats-grid">
          <div className="stat-item">
            <span className="stat-value">{formatNumber(repository.stars)}</span>
            <span className="stat-label">Stars</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{formatNumber(repository.forks)}</span>
            <span className="stat-label">Forks</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{formatNumber(repository.total_commits)}</span>
            <span className="stat-label">Commits</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{repository.total_contributors}</span>
            <span className="stat-label">Contributors</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{formatDate(repository.created_at)}</span>
            <span className="stat-label">Initial Commit</span>
          </div>
        </div>

        {/* Language Breakdown Bar */}
        <div className="report-languages">
          <div className="language-bar">
            {Object.entries(repository.languages).map(([lang, pct]) => (
              <div
                key={lang}
                className="language-segment"
                style={{
                  flexGrow: pct,
                  backgroundColor: getLangColor(lang),
                }}
                title={`${lang} ${pct.toFixed(1)}%`}
              ></div>
            ))}
          </div>
          <div className="language-legend">
            {Object.entries(repository.languages).map(([lang, pct]) => (
              <div key={lang} className="language-legend-item">
                <span className="language-dot" style={{ backgroundColor: getLangColor(lang) }}></span>
                <span>{lang}</span>
                <span className="language-percent">{pct.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Report Sections */}
        <div className="report-sections">
          <div className="report-section">
            <OverviewSection summary={ai_summary} />
          </div>

          <div className="report-section">
            <div className="section-header">
              <span className="section-icon">🌳</span>
              <h2>Project Composition</h2>
            </div>
            <CompositionSection structure={structure} />
          </div>

          <div className="report-section">
            <ContributorSection contributors={contributors} />
          </div>

          <div className="report-section">
            <InsightsSection insights={insights} />
          </div>

          <div className="report-section">
            <PatternsSection patterns={patterns} />
          </div>

          <div className="report-section">
            <RecommendationsSection recommendations={recommendations} />
          </div>
        </div>
      </div>
    </div>
  );
}
