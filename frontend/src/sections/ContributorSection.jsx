import ContributorCard from './ContributorCard';
import './ContributorSection.css';

export default function ContributorSection({ contributors }) {
  return (
    <div className="contributor-section glass-card" id="contributor-section">
      <h2 className="section-title">
        <span className="icon">👥</span>
        Contributor Intelligence
        <span style={{ 
          fontSize: 'var(--fs-sm)', 
          color: 'var(--text-muted)', 
          fontWeight: 'var(--fw-regular)',
          marginLeft: 'auto' 
        }}>
          {contributors.length} contributors analyzed
        </span>
      </h2>

      <div className="contributor-grid stagger-children">
        {contributors.map((contributor) => (
          <ContributorCard key={contributor.username} contributor={contributor} />
        ))}
      </div>
    </div>
  );
}
