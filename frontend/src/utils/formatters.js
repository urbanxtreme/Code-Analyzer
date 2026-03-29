/**
 * Format a large number with K/M suffixes
 * e.g., 1500 → "1.5K", 1200000 → "1.2M"
 */
export function formatNumber(num) {
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
  if (num >= 1_000) return (num / 1_000).toFixed(1).replace(/\.0$/, '') + 'K';
  return num.toString();
}

/**
 * Format a date string to a readable format
 * e.g., "2024-01-15T10:30:00Z" → "Jan 15, 2024"
 */
export function formatDate(dateStr) {
  if (!dateStr) return 'N/A';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

/**
 * Format a date to relative time
 * e.g., "2 days ago", "3 months ago"
 */
export function formatRelativeTime(dateStr) {
  if (!dateStr) return 'N/A';
  const now = new Date();
  const date = new Date(dateStr);
  const diffMs = now - date;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
  return `${Math.floor(diffDays / 365)} years ago`;
}

/**
 * Get quality tier based on score
 */
export function getQualityTier(score) {
  if (score >= 80) return { label: 'Excellent', color: '#10b981' };
  if (score >= 60) return { label: 'Good', color: '#06b6d4' };
  if (score >= 40) return { label: 'Fair', color: '#f59e0b' };
  return { label: 'Poor', color: '#ef4444' };
}

/**
 * Get risk badge class
 */
export function getRiskBadgeClass(level) {
  switch (level) {
    case 'low': return 'badge-success';
    case 'medium': return 'badge-warning';
    case 'high': return 'badge-danger';
    default: return 'badge-info';
  }
}

/**
 * Truncate a string with ellipsis
 */
export function truncate(str, maxLength = 80) {
  if (!str || str.length <= maxLength) return str;
  return str.substring(0, maxLength) + '...';
}

/**
 * Calculate percentage
 */
export function calcPercentage(value, total) {
  if (!total) return 0;
  return Math.round((value / total) * 100);
}

/**
 * Extract owner and repo from GitHub URL
 */
export function parseGitHubUrl(url) {
  const cleaned = url.trim().replace(/\/+$/, '');
  const match = cleaned.match(/github\.com\/([^/]+)\/([^/]+)/);
  if (match) return { owner: match[1], repo: match[2] };
  return null;
}

/**
 * Generate a color from a string (for avatars)
 */
export function stringToColor(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const h = hash % 360;
  return `hsl(${h}, 65%, 55%)`;
}
