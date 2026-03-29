// API base URL — will point to FastAPI backend
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Personality labels with emoji and color
export const PERSONALITY_MAP = {
  architect: { emoji: '🏗️', label: 'Architect', color: '#8b5cf6', description: 'Designs and builds core systems' },
  workhorse: { emoji: '🐴', label: 'Workhorse', color: '#06b6d4', description: 'Consistently high output' },
  perfectionist: { emoji: '✨', label: 'Perfectionist', color: '#ec4899', description: 'High code quality, detailed commits' },
  nightowl: { emoji: '🦉', label: 'Night Owl', color: '#6366f1', description: 'Prefers late-night coding sessions' },
  sprinter: { emoji: '⚡', label: 'Sprinter', color: '#f59e0b', description: 'Bursts of intense activity' },
  mentor: { emoji: '🎓', label: 'Mentor', color: '#10b981', description: 'Reviews PRs and guides others' },
  explorer: { emoji: '🧭', label: 'Explorer', color: '#14b8a6', description: 'Touches many parts of the codebase' },
  specialist: { emoji: '🎯', label: 'Specialist', color: '#f97316', description: 'Deep expertise in specific areas' },
  newcomer: { emoji: '🌱', label: 'Newcomer', color: '#84cc16', description: 'Recently joined, still ramping up' },
  ghost: { emoji: '👻', label: 'Ghost', color: '#6b7280', description: 'Infrequent or disappeared contributor' },
};

// Risk levels
export const RISK_LEVELS = {
  low: { label: 'Low Risk', color: '#10b981', bg: 'rgba(16,185,129,0.1)' },
  medium: { label: 'Medium Risk', color: '#f59e0b', bg: 'rgba(245,158,11,0.1)' },
  high: { label: 'High Risk', color: '#ef4444', bg: 'rgba(239,68,68,0.1)' },
};

// Commit quality tiers
export const QUALITY_TIERS = {
  excellent: { min: 80, label: 'Excellent', color: '#10b981' },
  good: { min: 60, label: 'Good', color: '#06b6d4' },
  fair: { min: 40, label: 'Fair', color: '#f59e0b' },
  poor: { min: 0, label: 'Poor', color: '#ef4444' },
};

// Loading steps shown during analysis
export const LOADING_STEPS = [
  { id: 'validate', label: 'Validating repository URL', icon: '🔗' },
  { id: 'fetch_meta', label: 'Fetching repository metadata', icon: '📋' },
  { id: 'fetch_commits', label: 'Collecting commit history', icon: '📝' },
  { id: 'fetch_contributors', label: 'Loading contributor data', icon: '👥' },
  { id: 'fetch_tree', label: 'Mapping file structure', icon: '🌳' },
  { id: 'analyze', label: 'Analyzing contribution patterns', icon: '🔍' },
  { id: 'ai_insights', label: 'Generating AI insights', icon: '🤖' },
  { id: 'report', label: 'Building intelligence report', icon: '📊' },
];

// Days of week labels
export const DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

// Hours labels
export const HOURS_OF_DAY = Array.from({ length: 24 }, (_, i) =>
  i === 0 ? '12am' : i < 12 ? `${i}am` : i === 12 ? '12pm' : `${i - 12}pm`
);
