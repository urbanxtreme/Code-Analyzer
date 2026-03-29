import { DAYS_OF_WEEK, HOURS_OF_DAY } from '../utils/constants';
import './PatternsSection.css';

function getHeatmapColor(value, max) {
  const intensity = max > 0 ? value / max : 0;
  if (intensity === 0) return 'rgba(139, 92, 246, 0.05)';
  if (intensity < 0.25) return 'rgba(139, 92, 246, 0.15)';
  if (intensity < 0.5) return 'rgba(139, 92, 246, 0.35)';
  if (intensity < 0.75) return 'rgba(139, 92, 246, 0.55)';
  return 'rgba(139, 92, 246, 0.85)';
}

export default function PatternsSection({ patterns }) {
  const { hourly_distribution, daily_distribution, commit_frequency } = patterns;

  const maxHourly = Math.max(...hourly_distribution);
  const maxDaily = Math.max(...daily_distribution);
  const maxMonthly = Math.max(...commit_frequency.data);

  return (
    <div className="patterns-section glass-card" id="patterns-section">
      <h2 className="section-title">
        <span className="icon">📊</span>
        Contribution Patterns
      </h2>

      <div className="patterns-grid">
        {/* Hourly Heatmap */}
        <div className="pattern-card">
          <div className="pattern-card-title">🕐 Commits by Hour of Day</div>
          <div className="heatmap-row">
            {hourly_distribution.map((val, i) => (
              <div
                key={i}
                className="heatmap-cell"
                style={{ backgroundColor: getHeatmapColor(val, maxHourly) }}
                title={`${HOURS_OF_DAY[i]}: ${val} commits`}
              >
                {val > 0 ? val : ''}
              </div>
            ))}
          </div>
          <div className="heatmap-labels">
            {HOURS_OF_DAY.filter((_, i) => i % 2 === 0).map((label, i) => (
              <div key={i} className="heatmap-label" style={{ gridColumn: `span 2` }}>
                {label}
              </div>
            ))}
          </div>
        </div>

        {/* Daily Bar Chart */}
        <div className="pattern-card">
          <div className="pattern-card-title">📅 Commits by Day of Week</div>
          <div className="bar-chart">
            {daily_distribution.map((val, i) => {
              const heightPct = maxDaily > 0 ? (val / maxDaily) * 100 : 0;
              return (
                <div key={i} className="bar-chart-item">
                  <div
                    className="bar"
                    style={{
                      height: `${heightPct}%`,
                      background: i === 0 || i === 6
                        ? 'linear-gradient(to top, rgba(139,92,246,0.3), rgba(139,92,246,0.5))'
                        : 'linear-gradient(to top, var(--primary), var(--secondary))',
                    }}
                    title={`${DAYS_OF_WEEK[i]}: ${val} commits`}
                  ></div>
                  <span className="bar-label">{DAYS_OF_WEEK[i]}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Monthly Commit Frequency */}
        <div className="pattern-card" style={{ gridColumn: '1 / -1' }}>
          <div className="pattern-card-title">📈 Monthly Commit Frequency</div>
          <div className="monthly-chart">
            {commit_frequency.data.map((val, i) => {
              const heightPct = maxMonthly > 0 ? (val / maxMonthly) * 100 : 0;
              return (
                <div key={i} className="monthly-bar-wrapper">
                  <div
                    className="monthly-bar"
                    style={{ height: `${heightPct}%` }}
                    title={`${commit_frequency.labels[i]}: ${val} commits`}
                  ></div>
                  <span className="monthly-label">{commit_frequency.labels[i]}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
