from typing import List, Dict, Any, Optional
from ..api.schemas import FinalReport, RepositoryMetadata, ContributorStats, Patterns, ProjectStructure
from ..analytics.file_analyzer import analyze_project_structure
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
    
    # 1. Analyze Project Structure
    structure_result = analyze_project_structure(raw_data.get("tree", []))
    
    # 2. Calculate Health Score (Basic MVP Heuristic)
    stars = meta.get("stargazers_count", 0)
    forks = meta.get("forks_count", 0)
    issues = meta.get("open_issues_count", 0)
    
    health_score = 75.0 # Default
    if stars > 0:
        issue_ratio = issues / stars
        # Lower ratio is generally better
        if issue_ratio < 0.05: health_score += 15
        elif issue_ratio < 0.1: health_score += 5
        elif issue_ratio > 0.5: health_score -= 20
    
    if forks > (stars / 5): health_score += 5 # High fork ratio
    
    # 3. Last commit days ago
    last_commit_days = 0
    commits = raw_data.get("commits", [])
    if commits:
        latest_date_str = commits[0].get("commit", {}).get("author", {}).get("date")
        if latest_date_str:
            latest_dt = datetime.strptime(latest_date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            last_commit_days = (datetime.now(timezone.utc) - latest_dt).days

    # 4. License and Topics
    license_name = meta.get("license", {}).get("name") if meta.get("license") else None
    repo_topics = meta.get("topics", [])

    # Repository Metadata Model
    repo_meta = RepositoryMetadata(
        name=meta.get("name"),
        owner=meta.get("owner", {}).get("login"),
        full_name=meta.get("full_name"),
        description=meta.get("description"),
        url=meta.get("html_url"),
        stars=stars,
        forks=forks,
        open_issues=issues,
        watchers=meta.get("watchers_count", 0),
        default_branch=meta.get("default_branch", "main"),
        created_at=datetime.strptime(meta.get("created_at"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc),
        updated_at=datetime.strptime(meta.get("updated_at"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc),
        languages=lang_pcts,
        topics=repo_topics,
        license=license_name,
        total_commits=len(commits),
        total_contributors=len(raw_data.get("contributors", [])),
        health_score=min(max(health_score, 0), 100),
        open_issues_to_stars_ratio=issues / stars if stars > 0 else 0,
        last_commit_days_ago=last_commit_days
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
        structure=structure_result,
        generated_at=datetime.now(timezone.utc)
    )
    
    return report
