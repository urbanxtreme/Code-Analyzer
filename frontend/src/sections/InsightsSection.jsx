import './InsightsSection.css';

export default function InsightsSection({ insights }) {
  return (
    <div className="insights-section glass-card" id="insights-section">
      <h2 className="section-title">
        <span className="icon">💡</span>
        Key Insights
      </h2>

      <div className="insights-grid">
        {/* Strengths */}
        <div className="insights-column">
          <div className="insights-column-header strengths">
            ✅ Strengths ({insights.strengths.length})
          </div>
          {insights.strengths.map((item, i) => (
            <div key={i} className="insight-item strength-item">
              {item}
            </div>
          ))}
        </div>

        {/* Weaknesses */}
        <div className="insights-column">
          <div className="insights-column-header weaknesses">
            ⚠️ Weaknesses ({insights.weaknesses.length})
          </div>
          {insights.weaknesses.map((item, i) => (
            <div key={i} className="insight-item weakness-item">
              {item}
            </div>
          ))}
        </div>

        {/* Risks */}
        <div className="insights-column">
          <div className="insights-column-header risks">
            🚨 Risks ({insights.risks.length})
          </div>
          {insights.risks.map((item, i) => (
            <div key={i} className="insight-item risk-item">
              {item}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
