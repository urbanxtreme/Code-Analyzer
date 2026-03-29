import React from 'react';
import './CompositionSection.css';

const EXTENSION_THEMES = {
  '.js': { label: 'JavaScript', color: '#f1e05a' },
  '.jsx': { label: 'React JS', color: '#61dafb' },
  '.ts': { label: 'TypeScript', color: '#3178c6' },
  '.tsx': { label: 'React TS', color: '#2b7489' },
  '.py': { label: 'Python', color: '#3572A5' },
  '.css': { label: 'CSS', color: '#563d7c' },
  '.html': { label: 'HTML', color: '#e34c26' },
  '.md': { label: 'Markdown', color: '#083fa1' },
  '.json': { label: 'JSON', color: '#292929' },
  '.yml': { label: 'YAML', color: '#cb171e' },
  '.yaml': { label: 'YAML', color: '#cb171e' },
  '.go': { label: 'Go', color: '#00ADD8' },
  '.rs': { label: 'Rust', color: '#dea584' },
};

export default function CompositionSection({ structure }) {
  const { extension_counts, total_files, folder_counts, documentation_status } = structure;

  // Sort extensions by count
  const sortedExts = Object.entries(extension_counts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 8); // Top 8

  return (
    <div className="composition-grid">
      <div className="composition-card main-stats">
        <div className="complexity-meter">
          <div className="meter-header">
            <span className="meter-label">Total Files</span>
            <span className="meter-value">{total_files}</span>
          </div>
          <div className="meter-bar">
            {sortedExts.map(([ext, count]) => (
              <div 
                key={ext}
                className="meter-segment"
                style={{ 
                  width: `${(count / total_files) * 100}%`,
                  backgroundColor: EXTENSION_THEMES[ext]?.color || '#6b7280'
                }}
                title={`${ext}: ${count} files`}
              ></div>
            ))}
          </div>
        </div>

        <div className="ext-legend">
          {sortedExts.map(([ext, count]) => (
            <div key={ext} className="ext-item">
              <span className="ext-dot" style={{ backgroundColor: EXTENSION_THEMES[ext]?.color || '#6b7280' }}></span>
              <span className="ext-name">{EXTENSION_THEMES[ext]?.label || ext}</span>
              <span className="ext-count">{count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="composition-card density-card">
        <h3>Codebase Density</h3>
        <div className="density-stats">
          <div className="density-item">
            <span className="density-label">Structure</span>
            <span className="density-value">{Object.keys(folder_counts).length} Root Folders</span>
          </div>
          <div className="density-item">
            <span className="density-label">Documentation</span>
            <span className={`density-status status-${documentation_status}`}>
              {documentation_status.toUpperCase()}
            </span>
          </div>
        </div>
        <div className="folder-list">
          {Object.keys(folder_counts).slice(0, 5).map(folder => (
            <span key={folder} className="folder-tag">📁 {folder}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
