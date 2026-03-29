from typing import List, Dict, Any, Optional
from ..api.schemas import FinalReport, RepositoryMetadata, ContributorStats, Patterns
from datetime import datetime, timezone

def build_report(raw_data: Dict[str, Any], analytics_result: List[ContributorStats], insights: Optional[Dict[str, Any]] = None) -> FinalReport:
    """
    Assembles the final intelligence report.
    Combines repository metadata, contributor stats, and generated insights.
    """
    meta = raw_data.get("metadata", {})
    languages = raw_data.get("languages", {})
    
    # Calculate language percentages
    total_size = sum(languages.values())
    lang_pcts = {lang: (size / total_size) * 100 for lang, size in languages.items()} if total_size > 0 else {}
    
    # Repository Metadata Model
    repo_meta = RepositoryMetadata(
        name=meta.get("name"),
        owner=meta.get("owner", {}).get("login"),
        full_name=meta.get("full_name"),
        description=meta.get("description"),
        url=meta.get("html_url"),
        stars=meta.get("stargazers_count", 0),
        forks=meta.get("forks_count", 0),
        open_issues=meta.get("open_issues_count", 0),
        watchers=meta.get("watchers_count", 0),
        default_branch=meta.get("default_branch", "main"),
        created_at=datetime.strptime(meta.get("created_at"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc),
        updated_at=datetime.strptime(meta.get("updated_at"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc),
        languages=lang_pcts,
        total_commits=len(raw_data.get("commits", [])),
        total_contributors=len(raw_data.get("contributors", []))
    )
    
    # AI Summary Model (MVP Mock Version)
    ai_summary = {
        "project_explanation": insights.get("project_explanation") if insights else "Analysis of " + meta.get("full_name") + " codebase history and contributor patterns.",
        "team_behavior": insights.get("team_behavior") if insights else "Collaborative development with " + str(len(raw_data.get("contributors", []))) + " active members.",
        "overall_health": "excellent" if repo_meta.stars > 1000 else "good"
    }
    
    # Insights Model (MVP Mock Version)
    final_insights = {
        "strengths": insights.get("strengths") if insights else ["Extensive commit history", "Healthy contributor base"],
        "weaknesses": insights.get("weaknesses") if insights else ["Documentation gap indicated in commit messages"],
        "risks": insights.get("risks") if insights else ["Low recent activity check"]
    }
    
    # Recommendations Model (MVP Mock Version)
    recommendations = []
    
    # Mock some recommendations based on contributor count
    if len(analytics_result) > 0:
        recommendations.append({
            "type": "positive",
            "target": analytics_result[0].username,
            "title": "Maintain High Ownership",
            "detail": "Continue leading the development based on your high contribution counts."
        })
    
    # Patterns Model (MVP Mock Version)
    patterns = Patterns(
        hourly_distribution=[0] * 24,
        daily_distribution=[0] * 7,
        commit_frequency={"labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], "data": [0] * 12}
    )
    
    # Final Report assembly
    report = FinalReport(
        repository=repo_meta,
        ai_summary=ai_summary,
        contributors=analytics_result,
        insights=final_insights,
        recommendations=recommendations,
        patterns=patterns,
        generated_at=datetime.now(timezone.utc)
    )
    
    return report
