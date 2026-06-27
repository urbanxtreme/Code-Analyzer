"""
Commit message quality analyzer.

Scores each commit message on a 0–100 scale using four heuristics:
  1. Length score      — ideal length is 20–72 chars (git best practice)
  2. Specificity score — penalize vague words, reward technical terms
  3. Format score      — bonus for Conventional Commits prefix (feat:, fix:, etc.)
  4. Uniqueness score  — penalize repeated identical messages per contributor

Returns a per-contributor average quality score.
"""

import re
from typing import List, Dict, Any
from collections import Counter

# Words that strongly suggest lazy/vague commit messages
VAGUE_WORDS = {
    "fix", "fixes", "fixed", "update", "updates", "updated",
    "change", "changes", "changed", "stuff", "things", "misc",
    "wip", "temp", "test", "testing", "commit", "work",
    "minor", "tweaks", "tweak", "clean", "cleanup", "cleanup",
    "edit", "edits", "editted", "edited", "done", "final",
}

# Words that suggest a meaningful, technical commit message
TECHNICAL_WORDS = {
    "implement", "add", "remove", "refactor", "improve", "optimize",
    "fix", "resolve", "close", "introduce", "migrate", "upgrade",
    "deprecate", "revert", "merge", "release", "bump", "support",
    "handle", "prevent", "ensure", "allow", "replace", "extract",
    "rename", "move", "split", "consolidate", "validate", "sanitize",
    "performance", "security", "authentication", "authorization",
    "api", "endpoint", "schema", "database", "cache", "async",
    "test", "spec", "coverage", "ci", "cd", "deploy", "build",
}

# Conventional Commits prefixes
CONVENTIONAL_PREFIXES = re.compile(
    r"^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert|wip)"
    r"(\(.+?\))?!?:\s+.+",
    re.IGNORECASE,
)


def score_commit_message(message: str) -> int:
    """
    Score a single commit message on a 0–100 scale.

    Components (weights):
      - Length score:      30 pts
      - Specificity score: 40 pts
      - Format score:      30 pts
    """
    if not message:
        return 0

    msg = message.strip()
    # Use only the first line (subject line)
    subject = msg.split("\n")[0].strip()
    length = len(subject)

    # ── 1. Length score (30 pts) ──────────────────────────────
    if length == 0:
        length_score = 0
    elif length < 10:
        length_score = 5
    elif length < 20:
        length_score = 15
    elif length <= 72:
        length_score = 30    # ideal range
    elif length <= 100:
        length_score = 20
    elif length <= 200:
        length_score = 10
    else:
        length_score = 5     # overly verbose

    # ── 2. Specificity score (40 pts) ────────────────────────
    words = set(re.findall(r"[a-z]+", subject.lower()))
    vague_hits = words & VAGUE_WORDS
    tech_hits = words & TECHNICAL_WORDS

    # Start at 20, +3 per technical word, -5 per vague-only word
    specificity_score = 20
    specificity_score += min(len(tech_hits) * 3, 20)    # cap bonus at +20
    specificity_score -= min(len(vague_hits) * 5, 20)   # cap penalty at -20

    # If the ENTIRE message is just one vague word, penalize hard
    if len(words) <= 2 and vague_hits:
        specificity_score = 0

    specificity_score = max(0, min(40, specificity_score))

    # ── 3. Format score (30 pts) ─────────────────────────────
    if CONVENTIONAL_PREFIXES.match(subject):
        format_score = 30   # Perfect conventional commit
    elif re.match(r"^[A-Z][^.!?]*[^.!? ]$", subject):
        format_score = 20   # Capitalised, no trailing punctuation
    elif length >= 15:
        format_score = 10   # At least a reasonable length
    else:
        format_score = 0

    total = length_score + specificity_score + format_score
    return min(100, max(0, total))


def analyze_commit_quality(
    commits: List[Dict[str, Any]],
    contributors: List[Dict[str, Any]],
) -> Dict[str, int]:
    """
    Compute the average commit quality score per contributor.

    Args:
        commits: Raw commit list from GitHub API.
        contributors: Raw contributor list from GitHub API (for username lookup).

    Returns:
        Dict mapping username -> average quality score (0–100).
    """
    # Map contributor login names for lookup
    known_users = {c.get("login") for c in contributors if c.get("login")}

    # Collect per-user message scores
    user_scores: Dict[str, List[int]] = {}

    for commit in commits:
        author = commit.get("author") or {}
        username = author.get("login")
        if not username or username not in known_users:
            continue

        message = commit.get("commit", {}).get("message", "")
        score = score_commit_message(message)

        if username not in user_scores:
            user_scores[username] = []
        user_scores[username].append(score)

    # ── Uniqueness penalty ────────────────────────────────────
    # Collect all messages per user; penalise repeated ones
    user_messages: Dict[str, List[str]] = {}
    for commit in commits:
        author = commit.get("author") or {}
        username = author.get("login")
        if not username or username not in known_users:
            continue
        subject = (commit.get("commit", {}).get("message", "") or "").split("\n")[0].strip().lower()
        user_messages.setdefault(username, []).append(subject)

    # Compute average per user, applying uniqueness penalty
    result: Dict[str, int] = {}
    for username, scores in user_scores.items():
        avg = sum(scores) / len(scores) if scores else 0

        # Uniqueness penalty: if >30% of messages are duplicates, reduce score
        messages = user_messages.get(username, [])
        if messages:
            counter = Counter(messages)
            duplicate_count = sum(v - 1 for v in counter.values() if v > 1)
            duplicate_ratio = duplicate_count / len(messages)
            if duplicate_ratio > 0.3:
                avg *= (1 - duplicate_ratio * 0.5)   # up to 50% reduction

        result[username] = int(min(100, max(0, round(avg))))

    return result
