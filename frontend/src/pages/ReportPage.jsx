import { formatNumber, formatDate } from '../utils/formatters';
import OverviewSection from '../sections/OverviewSection';
import ContributorSection from '../sections/ContributorSection';
import InsightsSection from '../sections/InsightsSection';
import PatternsSection from '../sections/PatternsSection';
import RecommendationsSection from '../sections/RecommendationsSection';
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
  const { repository, ai_summary, contributors, insights, recommendations, patterns } = report;

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
            <div className="report-meta">
              <div className="report-meta-item">
                ⭐ <span className="meta-value">{formatNumber(repository.stars)}</span> Stars
              </div>
              <div className="report-meta-item">
                🍴 <span className="meta-value">{formatNumber(repository.forks)}</span> Forks
              </div>
              <div className="report-meta-item">
                📝 <span className="meta-value">{formatNumber(repository.total_commits)}</span> Commits
              </div>
              <div className="report-meta-item">
                👥 <span className="meta-value">{repository.total_contributors}</span> Contributors
              </div>
              <div className="report-meta-item">
                📅 Created <span className="meta-value">{formatDate(repository.created_at)}</span>
              </div>
            </div>
          </div>

          <div className="report-header-right">
            <button className="report-back-btn" onClick={onReset} id="report-back-btn">
              ← New Analysis
            </button>
            <div className={`report-health-badge health-${ai_summary.overall_health}`}>
              {ai_summary.overall_health === 'excellent' && '🟢 '}
              {ai_summary.overall_health === 'good' && '🔵 '}
              {ai_summary.overall_health === 'fair' && '🟡 '}
              {ai_summary.overall_health === 'poor' && '🔴 '}
              {ai_summary.overall_health} Health
            </div>
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
                title={`${lang} ${pct}%`}
              ></div>
            ))}
          </div>
          <div className="language-legend">
            {Object.entries(repository.languages).map(([lang, pct]) => (
              <div key={lang} className="language-legend-item">
                <span className="language-dot" style={{ backgroundColor: getLangColor(lang) }}></span>
                <span>{lang}</span>
                <span className="language-percent">{pct}%</span>
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
