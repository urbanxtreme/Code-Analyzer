from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional, Any
from datetime import datetime

class AnalysisRequest(BaseModel):
    """Request model for analyzing a GitHub repository."""
    repo_url: str  # Can be a full URL or owner/repo shorthand

class RepositoryMetadata(BaseModel):
    """Repository information from GitHub."""
    name: str
    owner: str
    full_name: str
    description: Optional[str] = None
    url: str
    stars: int
    forks: int
    open_issues: int
    watchers: int
    default_branch: str
    created_at: datetime
    updated_at: datetime
    languages: Dict[str, float]
    topics: List[str] = []
    license: Optional[str] = None
    total_commits: int
    total_contributors: int
    health_score: float = 0.0
    open_issues_to_stars_ratio: float = 0.0
    last_commit_days_ago: int = 0

class ProjectStructure(BaseModel):
    """Breakdown of repository complexity and file types."""
    extension_counts: Dict[str, int]
    total_files: int
    folder_counts: Dict[str, int]
    documentation_status: str  # 'excellent', 'good', 'fair', 'poor'

class ContributorStats(BaseModel):
    """Statistics for an individual contributor."""
    username: str
    avatar_url: Optional[str] = None
    commits: int
    lines_added: int
    lines_removed: int
    commit_quality_score: int
    personality: str
    ai_code_likelihood: int
    risk_level: str
    contribution_pattern: str
    first_commit: datetime
    last_commit: datetime
    active_days: int
    avg_commits_per_week: float
    top_files: List[str]
    strengths: List[str]
    concerns: List[str]

class AIInsights(BaseModel):
    """AI-generated insights for the repository."""
    project_explanation: str
    team_behavior: str
    overall_health: str
    strengths: List[str]
    weaknesses: List[str]
    risks: List[str]

class Recommendation(BaseModel):
    """Actionable recommendation from AI."""
    type: str  # 'positive', 'warning', 'critical', 'general'
    target: str
    title: str
    detail: str

class Patterns(BaseModel):
    """Time-based contribution patterns."""
    hourly_distribution: List[int]
    daily_distribution: List[int]
    commit_frequency: Dict[str, Any]  # { "labels": [...], "data": [...] }

class FinalReport(BaseModel):
    """Full intelligence report for the repository."""
    repository: RepositoryMetadata
    ai_summary: Dict[str, str]  # { "project_explanation": "...", "team_behavior": "...", "overall_health": "..." }
    contributors: List[ContributorStats]
    insights: Dict[str, List[str]]  # { "strengths": [...], "weaknesses": [...], "risks": [...] }
    recommendations: List[Recommendation]
    patterns: Patterns
    structure: ProjectStructure
    generated_at: datetime
