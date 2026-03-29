import { formatNumber, getQualityTier, getRiskBadgeClass, stringToColor } from '../utils/formatters';
import { PERSONALITY_MAP } from '../utils/constants';
import './ContributorCard.css';

export default function ContributorCard({ contributor }) {
  const {
    username,
    avatar_url,
    commits,
    lines_added,
    lines_removed,
    commit_quality_score,
    personality,
    ai_code_likelihood,
    risk_level,
    strengths = [],
    concerns = [],
  } = contributor;

  const personalityInfo = PERSONALITY_MAP[personality] || PERSONALITY_MAP.explorer;
  const qualityTier = getQualityTier(commit_quality_score);
  const riskBadgeClass = getRiskBadgeClass(risk_level);

  return (
    <div
      className="contributor-card"
      style={{ '--card-accent': personalityInfo.color }}
      id={`contributor-${username}`}
    >
      {/* Header */}
      <div className="cc-header">
        {avatar_url ? (
          <img
            src={avatar_url}
            alt={username}
            className="cc-avatar"
            loading="lazy"
          />
        ) : (
          <div
            className="cc-avatar-placeholder"
            style={{ backgroundColor: stringToColor(username) }}
          >
            {username[0].toUpperCase()}
          </div>
        )}

        <div className="cc-info">
          <div className="cc-username">
            <a
              href={`https://github.com/${username}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {username}
            </a>
          </div>
          <div
            className="cc-personality"
            style={{ color: personalityInfo.color }}
          >
            {personalityInfo.emoji} {personalityInfo.label}
          </div>
        </div>

        <span className={`badge cc-risk-badge ${riskBadgeClass}`}>
          {risk_level}
        </span>
      </div>

      {/* Stats */}
      <div className="cc-stats">
        <div className="cc-stat">
          <div className="cc-stat-value">{formatNumber(commits)}</div>
          <div className="cc-stat-label">Commits</div>
        </div>
        <div className="cc-stat">
          <div className="cc-stat-value" style={{ color: 'var(--success)' }}>
            +{formatNumber(lines_added)}
          </div>
          <div className="cc-stat-label">Added</div>
        </div>
        <div className="cc-stat">
          <div className="cc-stat-value" style={{ color: 'var(--danger)' }}>
            -{formatNumber(lines_removed)}
          </div>
          <div className="cc-stat-label">Removed</div>
        </div>
      </div>

      {/* Commit Quality */}
      <div className="cc-quality">
        <div className="cc-quality-header">
          <span className="cc-quality-label">Commit Quality</span>
          <span
            className="cc-quality-value"
            style={{ color: qualityTier.color }}
          >
            {commit_quality_score}/100
          </span>
        </div>
        <div className="progress-bar">
          <div
            className="progress-bar-fill"
            style={{
              width: `${commit_quality_score}%`,
              background: qualityTier.color,
            }}
          ></div>
        </div>
      </div>

      {/* AI Estimate */}
      <div className="cc-ai-estimate">
        <span className="cc-ai-label">🤖 AI Code Estimate</span>
        <span
          className="cc-ai-value"
          style={{
            color:
              ai_code_likelihood > 25
                ? 'var(--danger)'
                : ai_code_likelihood > 10
                ? 'var(--warning)'
                : 'var(--success)',
          }}
        >
          ~{ai_code_likelihood}%
        </span>
      </div>

      {/* Tags */}
      <div className="cc-tags">
        {strengths.slice(0, 2).map((s, i) => (
          <span key={`s-${i}`} className="cc-tag strength">
            ✓ {s.length > 30 ? s.substring(0, 30) + '...' : s}
          </span>
        ))}
        {concerns.slice(0, 2).map((c, i) => (
          <span key={`c-${i}`} className="cc-tag concern">
            ⚠ {c.length > 30 ? c.substring(0, 30) + '...' : c}
          </span>
        ))}
      </div>
    </div>
  );
}
