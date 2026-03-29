import { LOADING_STEPS } from '../utils/constants';
import './LoadingState.css';

export default function LoadingState({ currentStep }) {
  const totalSteps = LOADING_STEPS.length;
  const progressPercent = Math.round(((currentStep + 1) / totalSteps) * 100);

  return (
    <div className="loading-overlay" id="loading-state">
      <div className="loading-brain">
        <div className="loading-ring"></div>
        <div className="loading-ring"></div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
          <span className="loading-brain-icon">🧠</span>
        </div>
      </div>

      <h2 className="loading-title">Analyzing Repository</h2>
      <p className="loading-subtitle">Our AI is investigating the codebase...</p>

      <div className="loading-steps">
        {LOADING_STEPS.map((step, index) => {
          const isDone = index < currentStep;
          const isActive = index === currentStep;

          return (
            <div
              key={step.id}
              className={`loading-step ${isActive ? 'step-active' : ''} ${isDone ? 'step-done' : ''}`}
            >
              <span className="loading-step-icon">{step.icon}</span>
              <span className="loading-step-label">{step.label}</span>
              <span className="loading-step-status">
                {isDone && <span className="step-check">✓</span>}
                {isActive && <span className="step-spinner"></span>}
              </span>
            </div>
          );
        })}
      </div>

      <div className="loading-progress-bar">
        <div className="loading-progress-label">
          <span>Progress</span>
          <span>{progressPercent}%</span>
        </div>
        <div className="progress-bar">
          <div
            className="progress-bar-fill"
            style={{ width: `${progressPercent}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
