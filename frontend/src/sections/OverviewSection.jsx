import './OverviewSection.css';

export default function OverviewSection({ summary }) {
  return (
    <div className="overview-section glass-card" id="overview-section">
      <h2 className="section-title">
        <span className="icon">🧠</span>
        AI Summary
      </h2>

      <div className="overview-content">
        <div className="overview-card">
          <div className="overview-card-title">
            📖 What is this project?
          </div>
          <p className="overview-card-text">
            {summary.project_explanation}
          </p>
        </div>

        <div className="overview-card">
          <div className="overview-card-title">
            👥 Team Behavior
          </div>
          <p className="overview-card-text">
            {summary.team_behavior}
          </p>
        </div>
      </div>
    </div>
  );
}
