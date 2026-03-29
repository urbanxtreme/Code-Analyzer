from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import collections
from ..api.schemas import ContributorStats

def analyze_contributors(raw_data: Dict[str, Any]) -> List[ContributorStats]:
    """
    Performs basic analysis on contributors.
    Calculates commit counts, personality labels, and code quality (MVP version).
    """
    metadata = raw_data.get("metadata", {})
    languages = raw_data.get("languages", {})
    contributors = raw_data.get("contributors", [])
    commits = raw_data.get("commits", [])
    tree = raw_data.get("tree", [])

    # Dictionary for storing contributor-specific data
    cont_stats = {}

    # Initialize data for each contributor
    for cont in contributors:
        username = cont.get("login")
        if not username:
            continue
        
        cont_stats[username] = {
            "username": username,
            "avatar_url": cont.get("avatar_url"),
            "commits": 0,
            "lines_added": 0,
            "lines_removed": 0,
            "first_commit": None,
            "last_commit": None,
            "active_days": 1,
            "avg_commits_per_week": 0.0,
            "top_files": [],
            "strengths": [],
            "concerns": []
        }

    # Process commits to get per-contributor stats
    for commit in commits:
        author = commit.get("author")
        if not author:
            continue
        
        username = author.get("login")
        if not username:
            continue
        
        if username not in cont_stats:
            # Maybe a contributor not in the top list?
            continue
        
        # Increment commit count
        cont_stats[username]["commits"] += 1
        
        # Extract commit date
        commit_date_str = commit.get("commit", {}).get("author", {}).get("date")
        if commit_date_str:
            commit_date = datetime.strptime(commit_date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            
            # Track first and last commit
            if not cont_stats[username]["first_commit"] or commit_date < cont_stats[username]["first_commit"]:
                cont_stats[username]["first_commit"] = commit_date
            if not cont_stats[username]["last_commit"] or commit_date > cont_stats[username]["last_commit"]:
                cont_stats[username]["last_commit"] = commit_date

    # Finalize stats for each contributor
    final_contributors = []
    
    for username, stats in cont_stats.items():
        # Heuristics for personality label (MVP Version)
        personality = "explorer"
        if stats["commits"] > 50:
            personality = "architect"
        elif stats["commits"] > 20:
            personality = "workhorse"
        elif stats["commits"] < 5:
            personality = "newcomer"
            
        # Basic commit quality score (MVP Version: based on length/desc of commits)
        # Placeholder for now
        commit_quality_score = 85 if stats["commits"] > 10 else 60
        
        # Code generated estimate (Placeholder MVP Version)
        ai_code_likelihood = 10 if stats["commits"] > 5 else 30
        
        # Risk level assessment (Placeholder MVP Version)
        risk_level = "low"
        if stats["commits"] < 5:
            risk_level = "medium"
        elif stats["commits"] > 0:
            risk_level = "low"

        # Construct ContributorStats Pydantic model
        c_stat = ContributorStats(
            username=stats["username"],
            avatar_url=stats["avatar_url"],
            commits=stats["commits"],
            lines_added=0,  # Placeholder for lines changed (fetching per-commit diff is intensive)
            lines_removed=0,
            commit_quality_score=commit_quality_score,
            personality=personality,
            ai_code_likelihood=ai_code_likelihood,
            risk_level=risk_level,
            contribution_pattern="consistent" if stats["commits"] > 10 else "burst",
            first_commit=stats["first_commit"] or datetime.now(timezone.utc),
            last_commit=stats["last_commit"] or datetime.now(timezone.utc),
            active_days=stats["active_days"],
            avg_commits_per_week=stats["avg_commits_per_week"],
            top_files=stats["top_files"],
            strengths=stats["strengths"] if stats["strengths"] else ["Reliable contributor"],
            concerns=stats["concerns"]
        )
        
        if stats["commits"] > 0:
            final_contributors.append(c_stat)

    # Sort final contributors by commit count (desc)
    final_contributors.sort(key=lambda x: x.commits, reverse=True)
    
    return final_contributors
