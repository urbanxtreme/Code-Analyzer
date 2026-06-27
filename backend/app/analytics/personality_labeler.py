"""
Personality labeler for contributors.

Maps contributor stats to one of 10 personality archetypes based on a
weighted scoring system across multiple dimensions.

Labels:
  architect    — designs core systems, high commit count + broad file coverage
  workhorse    — steady, reliable, high volume output
  perfectionist — high commit quality score, careful messages
  night_owl    — majority of commits happen between 22:00–04:00 UTC
  sprinter     — short burst activity windows, then dormant
  mentor       — many PRs reviewed / low own commits (approximated)
  explorer     — touches many different directories
  specialist   — concentrated in one area of the codebase
  newcomer     — very recent first commit, low total commits
  ghost        — extremely infrequent, <3 commits in sample window
"""

from typing import List, Dict, Any


def assign_personality(
    username: str,
    commits: int,
    commit_quality_score: int,
    active_days: int,
    avg_commits_per_week: float,
    contribution_pattern: str,
    top_files: List[str],
    hourly_distribution: List[int],
    first_commit_days_ago: int,
) -> str:
    """
    Assign a personality label to a contributor.

    Args:
        username: GitHub login (unused currently, reserved for future overrides).
        commits: Total commits in the sample window.
        commit_quality_score: 0–100 quality score.
        active_days: Number of distinct days with activity.
        avg_commits_per_week: Float average.
        contribution_pattern: 'consistent', 'burst', or 'sporadic'.
        top_files: List of file paths most frequently touched.
        hourly_distribution: 24-element list of commit counts by UTC hour.
        first_commit_days_ago: Days since first commit in the repo.

    Returns:
        A string label from the 10 archetypes above.
    """

    # ── Ghost ───────────────────────────────────────────────
    if commits < 3:
        return "ghost"

    # ── Newcomer ────────────────────────────────────────────
    if first_commit_days_ago < 30 and commits < 20:
        return "newcomer"

    # ── Night Owl ───────────────────────────────────────────
    # Night hours: 22, 23, 0, 1, 2, 3, 4
    night_hours = [22, 23, 0, 1, 2, 3, 4]
    night_commits = sum(hourly_distribution[h] for h in night_hours if h < len(hourly_distribution))
    total_timed = sum(hourly_distribution)
    if total_timed > 0 and (night_commits / total_timed) > 0.45:
        return "night_owl"

    # ── Sprinter ────────────────────────────────────────────
    if contribution_pattern == "burst" and commits >= 10:
        return "sprinter"

    # ── Perfectionist ───────────────────────────────────────
    if commit_quality_score >= 85 and commits >= 10:
        return "perfectionist"

    # ── Architect ───────────────────────────────────────────
    # High commit count + broad file coverage (many different directories)
    unique_dirs = _count_unique_dirs(top_files)
    if commits >= 50 and unique_dirs >= 3:
        return "architect"

    # ── Workhorse ───────────────────────────────────────────
    if commits >= 30 and contribution_pattern == "consistent":
        return "workhorse"

    # ── Specialist ──────────────────────────────────────────
    if commits >= 10 and unique_dirs <= 2 and len(top_files) >= 3:
        return "specialist"

    # ── Explorer ────────────────────────────────────────────
    if unique_dirs >= 4:
        return "explorer"

    # ── Default fallback ────────────────────────────────────
    if commits >= 20:
        return "workhorse"
    if commits >= 10:
        return "explorer"
    return "newcomer"


def _count_unique_dirs(top_files: List[str]) -> int:
    """Count the number of unique top-level directories in top_files."""
    dirs = set()
    for path in top_files:
        parts = path.replace("\\", "/").split("/")
        if len(parts) > 1:
            dirs.add(parts[0])
        else:
            dirs.add("root")
    return len(dirs)


def assign_all_personalities(
    contributor_data: List[Dict[str, Any]],
    hourly_distribution: List[int],
) -> Dict[str, str]:
    """
    Assign personality labels to all contributors.

    Args:
        contributor_data: List of dicts, each containing contributor stats.
        hourly_distribution: Global repo-level hourly commit distribution.

    Returns:
        Dict mapping username -> personality label.
    """
    result: Dict[str, str] = {}
    for c in contributor_data:
        username = c.get("username", "")
        result[username] = assign_personality(
            username=username,
            commits=c.get("commits", 0),
            commit_quality_score=c.get("commit_quality_score", 50),
            active_days=c.get("active_days", 1),
            avg_commits_per_week=c.get("avg_commits_per_week", 0.0),
            contribution_pattern=c.get("contribution_pattern", "sporadic"),
            top_files=c.get("top_files", []),
            hourly_distribution=hourly_distribution,
            first_commit_days_ago=c.get("first_commit_days_ago", 365),
        )
    return result
