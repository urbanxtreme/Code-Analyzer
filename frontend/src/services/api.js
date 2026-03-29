import { API_BASE_URL } from '../utils/constants';

/**
 * API service for communicating with the FastAPI backend.
 * Currently returns mock data for frontend development.
 */

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  /**
   * Analyze a GitHub repository
   * @param {string} repoUrl - Full GitHub repository URL
   * @returns {Promise<Object>} - Analysis report
   */
  async analyzeRepository(repoUrl) {
    const response = await fetch(`${this.baseUrl}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_url: repoUrl }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Analysis failed (HTTP ${response.status})`);
    }

    return response.json();
  }

  /**
   * Check backend health
   * @returns {Promise<Object>} - Health status
   */
  async checkHealth() {
    const response = await fetch(`${this.baseUrl}/api/health`);
    if (!response.ok) throw new Error('Backend is not reachable');
    return response.json();
  }
}

const api = new ApiService();
export default api;
