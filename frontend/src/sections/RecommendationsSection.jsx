import './RecommendationsSection.css';

const TYPE_ICONS = {
  positive: '✅',
  warning: '⚠️',
  critical: '🚨',
  general: '💡',
};

export default function RecommendationsSection({ recommendations }) {
  return (
    <div className="recommendations-section glass-card" id="recommendations-section">
      <h2 className="section-title">
        <span className="icon">📋</span>
        AI Recommendations
      </h2>

      <div className="recommendations-list stagger-children">
        {recommendations.map((rec, i) => (
          <div key={i} className={`recommendation-card type-${rec.type}`}>
            <div className="rec-icon">
              {TYPE_ICONS[rec.type] || '💡'}
            </div>
            <div className="rec-content">
              <div className="rec-header">
                <span className="rec-title">{rec.title}</span>
                <span className="rec-target">@{rec.target}</span>
              </div>
              <p className="rec-detail">{rec.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
