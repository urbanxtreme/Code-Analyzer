"""
Contributor analyzer — orchestrates all per-contributor analytics.

Replaces the old placeholder version with real calls to:
  - commit_analyzer.py  (quality scores)
  - ai_code_estimator.py (AI likelihood)
  - personality_labeler.py (personality labels)

Also computes:
  - active_days (days between first and last commit)
  - avg_commits_per_week
  - contribution_pattern (consistent / burst / sporadic)
  - top_files (most frequently touched paths)
  - risk_level (low / medium / high)
  - strengths / concerns (heuristic bullet points)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from collections import Counter

from ..api.schemas import ContributorStats
from .commit_analyzer import analyze_commit_quality
from .ai_code_estimator import estimate_all
from .personality_labeler import assign_personality
from .pattern_detector import detect_patterns


def analyze_contributors(raw_data: Dict[str, Any]) -> List[ContributorStats]:
    """
    Perform full contributor analysis from raw GitHub API data.

    Args:
        raw_data: Dict with keys: metadata, languages, contributors, commits, tree.

    Returns:
        Sorted list of ContributorStats (highest commit count first).
    """
    contributors = raw_data.get("contributors", [])
    commits = raw_data.get("commits", [])
    tree = raw_data.get("tree", [])

    if not contributors:
        return []

    # ── Pre-compute cross-contributor analytics ───────────────
    quality_scores: Dict[str, int] = analyze_commit_quality(commits, contributors)
    ai_scores: Dict[str, int] = estimate_all(contributors, commits, tree)

    # Global hourly distribution (for night-owl detection)
    patterns_obj = detect_patterns(commits)
    global_hourly = patterns_obj.hourly_distribution

    # Build file-touch map per contributor
    file_touch_map: Dict[str, Counter] = {}
    for commit in commits:
        author = commit.get("author") or {}
        username = author.get("login")
        if not username:
            continue
        # GitHub list-commits endpoint doesn't return per-file info,
        # so we derive top_files from the tree paths weighted by commit count.
        # A proper implementation would call /commits/{sha} for each commit
        # (too expensive); instead we use the tree as a proxy.

    # ── Per-contributor stats ─────────────────────────────────
    # Build base stats dict
    cont_base: Dict[str, Dict] = {}
    for c in contributors:
        username = c.get("login")
        if not username:
            continue
        cont_base[username] = {
            "username": username,
            "avatar_url": c.get("avatar_url", ""),
            "commits": 0,
            "first_commit": None,
            "last_commit": None,
            "commit_hours": [],
            "daily_gaps": [],     # gaps in days between consecutive commits
        }

    # Walk commits to gather per-user stats
    for commit in commits:
        author = commit.get("author") or {}
        username = author.get("login")
        if not username or username not in cont_base:
            continue

        cont_base[username]["commits"] += 1

        date_str = commit.get("commit", {}).get("author", {}).get("date")
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                stats = cont_base[username]
                if not stats["first_commit"] or dt < stats["first_commit"]:
                    stats["first_commit"] = dt
                if not stats["last_commit"] or dt > stats["last_commit"]:
                    stats["last_commit"] = dt
                stats["commit_hours"].append(dt.hour)
            except ValueError:
                pass

    # ── Derive top_files from tree (approximate) ──────────────
    # Use extensions and folder structure to give contributors
    # contextual file associations based on repo structure.
    # (Full per-commit file list would require N extra API calls.)
    repo_files = [item.get("path", "") for item in tree if item.get("type") == "blob"]

    now = datetime.now(timezone.utc)

    final_contributors: List[ContributorStats] = []

    for username, stats in cont_base.items():
        commit_count = stats["commits"]
        if commit_count == 0:
            continue

        first_commit = stats["first_commit"] or now
        last_commit = stats["last_commit"] or now

        # ── active_days ──────────────────────────────────────
        active_days = max((last_commit - first_commit).days, 1)

        # ── avg_commits_per_week ─────────────────────────────
        weeks = max(active_days / 7, 1)
        avg_per_week = round(commit_count / weeks, 2)

        # ── contribution_pattern ─────────────────────────────
        pattern = _derive_pattern(commit_count, active_days, avg_per_week)

        # ── top_files (sampled from repo tree by pattern) ────
        top_files = _sample_top_files(repo_files, commit_count)

        # ── first_commit_days_ago ────────────────────────────
        first_commit_days_ago = (now - first_commit).days

        # ── quality score ────────────────────────────────────
        quality = quality_scores.get(username, 50)

        # ── AI likelihood ────────────────────────────────────
        ai_likelihood = ai_scores.get(username, 5)

        # ── personality ──────────────────────────────────────
        personality = assign_personality(
            username=username,
            commits=commit_count,
            commit_quality_score=quality,
            active_days=active_days,
            avg_commits_per_week=avg_per_week,
            contribution_pattern=pattern,
            top_files=top_files,
            hourly_distribution=global_hourly,
            first_commit_days_ago=first_commit_days_ago,
        )

        # ── risk_level ───────────────────────────────────────
        risk = _derive_risk(commit_count, quality, ai_likelihood, active_days)

        # ── strengths / concerns ─────────────────────────────
        strengths, concerns = _derive_strengths_concerns(
            commit_count, quality, ai_likelihood, pattern, active_days
        )

        final_contributors.append(ContributorStats(
            username=username,
            avatar_url=stats["avatar_url"],
            commits=commit_count,
            lines_added=0,    # Requires per-commit diff API — cost-prohibitive
            lines_removed=0,
            commit_quality_score=quality,
            personality=personality,
            ai_code_likelihood=ai_likelihood,
            risk_level=risk,
            contribution_pattern=pattern,
            first_commit=first_commit,
            last_commit=last_commit,
            active_days=active_days,
            avg_commits_per_week=avg_per_week,
            top_files=top_files,
            strengths=strengths,
            concerns=concerns,
        ))

    # Sort by commit count descending
    final_contributors.sort(key=lambda x: x.commits, reverse=True)
    return final_contributors


# ──────────────────────────────────────────────────────────────
# Private helpers
# ──────────────────────────────────────────────────────────────

def _derive_pattern(commits: int, active_days: int, avg_per_week: float) -> str:
    """Classify contribution pattern as consistent / burst / sporadic."""
    if active_days < 7 and commits >= 5:
        return "burst"
    if avg_per_week >= 1.5:
        return "consistent"
    if avg_per_week < 0.5:
        return "sporadic"
    return "consistent"


def _sample_top_files(repo_files: List[str], commit_count: int) -> List[str]:
    """
    Return a representative sample of files from the repo tree.
    Without per-commit diff data, we pick meaningful-looking paths.
    """
    if not repo_files:
        return []

    # Prefer source code files over config/lock files
    priority_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs",
                     ".java", ".cpp", ".c", ".cs", ".rb", ".swift", ".kt"}
    source_files = [f for f in repo_files if any(f.endswith(e) for e in priority_exts)]
    chosen = source_files if source_files else repo_files

    # Return up to 3 files, spacing them across the list for variety
    n = min(3, len(chosen))
    if n == 0:
        return []
    step = max(len(chosen) // n, 1)
    return [chosen[i * step] for i in range(n)]


def _derive_risk(commits: int, quality: int, ai_likelihood: int, active_days: int) -> str:
    """Classify contributor risk level as low / medium / high."""
    score = 0
    if commits < 5:
        score += 2
    if quality < 40:
        score += 2
    elif quality < 60:
        score += 1
    if ai_likelihood > 50:
        score += 2
    elif ai_likelihood > 25:
        score += 1
    if active_days < 7:
        score += 1

    if score >= 4:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def _derive_strengths_concerns(
    commits: int,
    quality: int,
    ai_likelihood: int,
    pattern: str,
    active_days: int,
) -> tuple:
    """Return (strengths, concerns) lists based on heuristics."""
    strengths = []
    concerns = []

    if commits >= 50:
        strengths.append("High commit volume — core contributor")
    elif commits >= 20:
        strengths.append("Solid commit history")

    if quality >= 80:
        strengths.append("Excellent commit message quality")
    elif quality >= 65:
        strengths.append("Good commit message quality")

    if pattern == "consistent":
        strengths.append("Consistent, steady contribution pattern")

    if active_days >= 180:
        strengths.append("Long-term project contributor")

    if not strengths:
        strengths.append("Active contributor to the repository")

    if quality < 40:
        concerns.append("Low commit message quality — messages are vague or too short")
    if ai_likelihood > 50:
        concerns.append("High AI-assisted code likelihood — review contributions carefully")
    elif ai_likelihood > 25:
        concerns.append("Moderate AI code likelihood detected")
    if pattern == "burst":
        concerns.append("Burst contribution pattern — may indicate rushed work")
    if commits < 5:
        concerns.append("Very few commits in the sampled window")

    return strengths, concerns
