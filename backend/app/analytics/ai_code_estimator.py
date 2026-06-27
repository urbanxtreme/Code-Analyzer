"""
Heuristic AI-vs-human code estimator.

DISCLAIMER: This is speculative and heuristic-based. It is NOT a definitive
classification. It identifies patterns that *may* correlate with AI-assisted
code generation but can have many other explanations.

Signals used:
  1. Burst pattern   — many commits in a short window then silence
  2. Large commits   — single commits with many files changed (hard to measure
                       without per-commit diff, so we proxy via commit frequency)
  3. Vague messages  — commit messages that look templated / overly formal
  4. Low uniqueness  — identical or near-identical commit messages
  5. Short history   — very short active period with high output

Returns a 0–100 likelihood score per contributor.
"""

import re
from typing import List, Dict, Any
from datetime import datetime, timezone
from collections import Counter

# Patterns that often appear in AI-generated or templated commit messages
AI_MESSAGE_PATTERNS = [
    re.compile(r"^(initial commit|init|first commit)$", re.IGNORECASE),
    re.compile(r"^(add|added|adding)\s+(files?|code|changes?)$", re.IGNORECASE),
    re.compile(r"^update\s+readme", re.IGNORECASE),
    re.compile(r"^(feat|fix|chore):\s*(implement|add|update)\s+\w+\s+(functionality|feature|module|component)$", re.IGNORECASE),
    re.compile(r"^wip\s*[-:]?\s*(work in progress)?$", re.IGNORECASE),
    re.compile(r"^(refactor|cleanup|clean up)\s+code$", re.IGNORECASE),
]

# File patterns commonly associated with auto-generated boilerplate
BOILERPLATE_EXTENSIONS = {
    ".lock", ".sum", ".min.js", ".min.css", ".pb.go", ".pb.py",
    ".generated.ts", ".g.dart", ".freezed.dart",
}

BOILERPLATE_FILENAMES = {
    "package-lock.json", "yarn.lock", "poetry.lock", "pipfile.lock",
    "go.sum", ".gitignore", ".editorconfig", ".prettierrc",
    "license", "licence", "copying",
}


def estimate_ai_likelihood(
    username: str,
    commits: List[Dict[str, Any]],
    tree: List[Dict[str, Any]],
) -> int:
    """
    Estimate the likelihood (0–100) that a contributor used AI assistance.

    Args:
        username: The contributor's GitHub login.
        commits: All commits from the repo (filtered to this user inside).
        tree: The repository file tree from GitHub API.

    Returns:
        An integer 0–100. Higher = more likely AI-assisted.
    """
    user_commits = [
        c for c in commits
        if (c.get("author") or {}).get("login") == username
    ]

    if not user_commits:
        return 0

    score = 0  # Accumulates penalty points

    # ── Signal 1: Message vagueness / template patterns ──────
    vague_count = 0
    messages = []
    for c in user_commits:
        msg = (c.get("commit", {}).get("message") or "").split("\n")[0].strip()
        messages.append(msg.lower())
        for pattern in AI_MESSAGE_PATTERNS:
            if pattern.match(msg):
                vague_count += 1
                break

    vague_ratio = vague_count / len(user_commits)
    if vague_ratio > 0.5:
        score += 30
    elif vague_ratio > 0.25:
        score += 15
    elif vague_ratio > 0.1:
        score += 5

    # ── Signal 2: Low message uniqueness (copy-paste / template) ──
    if messages:
        counter = Counter(messages)
        duplicate_count = sum(v - 1 for v in counter.values() if v > 1)
        duplicate_ratio = duplicate_count / len(messages)
        if duplicate_ratio > 0.5:
            score += 25
        elif duplicate_ratio > 0.3:
            score += 15
        elif duplicate_ratio > 0.1:
            score += 5

    # ── Signal 3: Burst activity pattern ─────────────────────
    dates = []
    for c in user_commits:
        date_str = c.get("commit", {}).get("author", {}).get("date")
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                dates.append(dt)
            except ValueError:
                pass

    if len(dates) >= 3:
        dates.sort()
        gaps_hours = [
            (dates[i + 1] - dates[i]).total_seconds() / 3600
            for i in range(len(dates) - 1)
        ]
        # Detect burst: many commits close together then long silence
        short_gaps = sum(1 for g in gaps_hours if g < 1)  # commits within 1 hour
        burst_ratio = short_gaps / len(gaps_hours)
        if burst_ratio > 0.6:
            score += 20
        elif burst_ratio > 0.4:
            score += 10

        # Very short overall active period with many commits
        active_days = max((dates[-1] - dates[0]).days, 1)
        commits_per_day = len(user_commits) / active_days
        if commits_per_day > 20 and active_days < 7:
            score += 15   # Extremely high output in very short time

    # ── Signal 4: Very short commit messages (all under 15 chars) ──
    short_msg_count = sum(1 for m in messages if len(m) < 15)
    if messages and (short_msg_count / len(messages)) > 0.6:
        score += 10

    return min(100, max(0, score))


def estimate_all(
    contributors: List[Dict[str, Any]],
    commits: List[Dict[str, Any]],
    tree: List[Dict[str, Any]],
) -> Dict[str, int]:
    """
    Compute AI likelihood scores for all known contributors.

    Returns:
        Dict mapping username -> likelihood score (0–100).
    """
    result: Dict[str, int] = {}
    for contributor in contributors:
        username = contributor.get("login")
        if username:
            result[username] = estimate_ai_likelihood(username, commits, tree)
    return result
