"""
Report builder — assembles the final FinalReport JSON.

Takes:
  - raw_data: raw GitHub API response dict
  - analytics_result: list of ContributorStats
  - llm_insights: LLMInsights object (real or fallback)

Produces the complete FinalReport Pydantic model.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from ..api.schemas import (
    FinalReport, RepositoryMetadata, ContributorStats,
    Patterns, ProjectStructure, Recommendation,
)
from ..analytics.file_analyzer import analyze_project_structure
from ..llm.models import LLMInsights


def build_report(
    raw_data: Dict[str, Any],
    analytics_result: List[ContributorStats],
    llm_insights: Optional[LLMInsights] = None,
) -> FinalReport:
    """Assemble the full intelligence report."""

    meta = raw_data.get("metadata", {})
    languages = raw_data.get("languages", {})
    commits = raw_data.get("commits", [])
    contributors_raw = raw_data.get("contributors", [])
    tree = raw_data.get("tree", [])

    # ── Language percentages ──────────────────────────────────
    total_size = sum(languages.values())
    lang_pcts: Dict[str, float] = (
        {lang: (size / total_size) * 100 for lang, size in languages.items()}
        if total_size > 0 else {}
    )

    # ── Project structure ─────────────────────────────────────
    structure_result: ProjectStructure = analyze_project_structure(tree)

    # ── Health score ──────────────────────────────────────────
    stars = meta.get("stargazers_count", 0)
    forks = meta.get("forks_count", 0)
    issues = meta.get("open_issues_count", 0)

    health_score = 75.0
    if stars > 0:
        issue_ratio = issues / stars
        if issue_ratio < 0.05:
            health_score += 15
        elif issue_ratio < 0.1:
            health_score += 5
        elif issue_ratio > 0.5:
            health_score -= 20
    if forks > (stars / 5):
        health_score += 5
    health_score = min(max(health_score, 0), 100)

    # ── Last commit days ago ──────────────────────────────────
    last_commit_days = 0
    if commits:
        latest_date_str = commits[0].get("commit", {}).get("author", {}).get("date")
        if latest_date_str:
            try:
                latest_dt = datetime.strptime(latest_date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                last_commit_days = (datetime.now(timezone.utc) - latest_dt).days
            except ValueError:
                pass

    # ── License & topics ─────────────────────────────────────
    license_name = meta.get("license", {}).get("name") if meta.get("license") else None
    repo_topics = meta.get("topics", [])

    # ── Repository metadata ───────────────────────────────────
    repo_meta = RepositoryMetadata(
        name=meta.get("name", "unknown"),
        owner=meta.get("owner", {}).get("login", "unknown"),
        full_name=meta.get("full_name", "unknown/unknown"),
        description=meta.get("description"),
        url=meta.get("html_url", ""),
        stars=stars,
        forks=forks,
        open_issues=issues,
        watchers=meta.get("watchers_count", 0),
        default_branch=meta.get("default_branch", "main"),
        created_at=_parse_dt(meta.get("created_at")),
        updated_at=_parse_dt(meta.get("updated_at")),
        languages=lang_pcts,
        topics=repo_topics,
        license=license_name,
        total_commits=len(commits),
        total_contributors=len(contributors_raw),
        health_score=health_score,
        open_issues_to_stars_ratio=issues / stars if stars > 0 else 0.0,
        last_commit_days_ago=last_commit_days,
    )

    # ── AI summary from LLM insights ─────────────────────────
    if llm_insights:
        ai_summary = {
            "project_explanation": llm_insights.project_explanation,
            "team_behavior": llm_insights.team_behavior,
            "overall_health": llm_insights.overall_health,
            "llm_available": str(llm_insights.llm_available),
            "model_used": llm_insights.model_used or "heuristic-fallback",
        }
        insights_dict = {
            "strengths": llm_insights.strengths,
            "weaknesses": llm_insights.weaknesses,
            "risks": llm_insights.risks,
        }
        recommendations = [
            Recommendation(
                type=r.type,
                target=r.target,
                title=r.title,
                detail=r.detail,
            )
            for r in llm_insights.recommendations
        ]
    else:
        # Pure heuristic fallback (no llm_insights object at all)
        ai_summary = {
            "project_explanation": (
                f"Analysis of {repo_meta.full_name} completed using heuristic methods. "
                "Install and run Ollama locally to enable AI-powered narrative insights."
            ),
            "team_behavior": (
                f"This repository has {repo_meta.total_contributors} contributor(s) "
                f"and {repo_meta.total_commits} commits in the sampled window."
            ),
            "overall_health": (
                "excellent" if health_score >= 80
                else "good" if health_score >= 60
                else "fair" if health_score >= 40
                else "poor"
            ),
            "llm_available": "false",
            "model_used": "heuristic-fallback",
        }
        insights_dict = {
            "strengths": ["Commit history available for analysis"],
            "weaknesses": ["AI-powered insights require Ollama to be running"],
            "risks": ["Manual review recommended"],
        }
        recommendations = _heuristic_recommendations(analytics_result)

    # ── Placeholder patterns (overridden in routes.py) ───────
    patterns = Patterns(
        hourly_distribution=[0] * 24,
        daily_distribution=[0] * 7,
        commit_frequency={
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "data": [0] * 12,
        },
    )

    return FinalReport(
        repository=repo_meta,
        ai_summary=ai_summary,
        contributors=analytics_result,
        insights=insights_dict,
        recommendations=recommendations,
        patterns=patterns,
        structure=structure_result,
        generated_at=datetime.now(timezone.utc),
    )


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _parse_dt(date_str: Optional[str]) -> datetime:
    if not date_str:
        return datetime.now(timezone.utc)
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.now(timezone.utc)


def _heuristic_recommendations(analytics_result: List[ContributorStats]) -> List[Recommendation]:
    """Generate basic recommendations from heuristics when LLM is unavailable."""
    recs: List[Recommendation] = []

    if analytics_result:
        top = analytics_result[0]
        recs.append(Recommendation(
            type="positive",
            target=top.username,
            title="Leading Contributor",
            detail=(
                f"{top.username} has the highest commit count ({top.commits}). "
                "Continue maintaining this level of contribution to keep the project moving."
            ),
        ))

    high_risk = [c for c in analytics_result if c.risk_level == "high"]
    for c in high_risk[:2]:
        recs.append(Recommendation(
            type="critical",
            target=c.username,
            title="High Risk Contributor — Review Needed",
            detail=(
                f"{c.username} has been flagged as high risk based on commit quality "
                f"({c.commit_quality_score}/100) and AI likelihood ({c.ai_code_likelihood}%). "
                "All contributions should be carefully reviewed."
            ),
        ))

    recs.append(Recommendation(
        type="general",
        target="team",
        title="Enable AI Insights",
        detail=(
            "Install Ollama and run 'ollama pull llama3.2:3b' to unlock AI-generated "
            "project explanations, team behavior analysis, and smart recommendations."
        ),
    ))

    return recs
