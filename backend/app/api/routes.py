"""
API routes for the AI Code Analyzer.

POST /analyze  — full synchronous analysis pipeline
GET  /health   — backend + Ollama status check
GET  /status/{id} — placeholder for future async job tracking
"""

import re
import logging
from fastapi import APIRouter, HTTPException

from .schemas import AnalysisRequest, FinalReport
from ..fetcher.github_client import GitHubClient
from ..analytics.contributor_analyzer import analyze_contributors
from ..analytics.pattern_detector import detect_patterns
from ..report.report_builder import build_report
from ..llm.ollama_client import OllamaClient
from ..llm.prompt_builder import build_analysis_prompt, build_fallback_insights
from ..llm.response_parser import parse_llm_response, insights_from_fallback
from ..utils.cache import cache

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory store for async job status (reserved for future SSE work)
analysis_store = {}


def _parse_repo_url(repo_url: str):
    """
    Extract (owner, repo) from a variety of GitHub URL formats.

    Supports:
      - https://github.com/owner/repo
      - https://github.com/owner/repo.git
      - github.com/owner/repo
      - owner/repo
    """
    url = repo_url.strip().rstrip("/")

    # Remove .git suffix
    if url.endswith(".git"):
        url = url[:-4]

    # Full URL pattern
    match = re.match(
        r"(?:https?://)?(?:www\.)?github\.com/([^/\s]+)/([^/\s#?]+)",
        url,
        re.IGNORECASE,
    )
    if match:
        return match.group(1), match.group(2)

    # owner/repo shorthand
    match = re.match(r"^([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)$", url)
    if match:
        return match.group(1), match.group(2)

    raise HTTPException(
        status_code=400,
        detail=(
            "Invalid repository URL. Please use one of these formats:\n"
            "  • https://github.com/owner/repo\n"
            "  • owner/repo"
        ),
    )


@router.post("/analyze", response_model=FinalReport)
async def analyze_repository(request: AnalysisRequest):
    """
    Full analysis pipeline:
      1. Parse & validate the repo URL
      2. Fetch data from GitHub (with caching)
      3. Run analytics engine
      4. Generate AI insights via Ollama (graceful fallback if unavailable)
      5. Assemble and return the final report
    """
    owner, repo = _parse_repo_url(request.repo_url)
    cache_key = f"analysis:{owner}/{repo}"

    # ── Check cache ───────────────────────────────────────────
    cached = cache.get(cache_key)
    if cached:
        logger.info("Cache hit for %s/%s", owner, repo)
        return cached

    try:
        # ── Phase 1: Data Collection ──────────────────────────
        logger.info("Fetching GitHub data for %s/%s", owner, repo)
        client = GitHubClient()
        raw_data = await client.fetch_repository_data(owner, repo)

        # ── Phase 2: Analytics ───────────────────────────────
        logger.info("Running analytics...")
        analytics_result = analyze_contributors(raw_data)
        patterns_result = detect_patterns(raw_data.get("commits", []))

        # ── Phase 3: AI Insights ─────────────────────────────
        logger.info("Generating AI insights...")
        ollama = OllamaClient()
        llm_insights = None

        # Build contributor summaries for the prompt
        contributor_summaries = [
            {
                "username": c.username,
                "commits": c.commits,
                "commit_quality_score": c.commit_quality_score,
                "personality": c.personality,
                "ai_code_likelihood": c.ai_code_likelihood,
                "contribution_pattern": c.contribution_pattern,
                "risk_level": c.risk_level,
            }
            for c in analytics_result
        ]

        meta = raw_data.get("metadata", {})
        stars = meta.get("stargazers_count", 0)
        forks = meta.get("forks_count", 0)
        issues = meta.get("open_issues_count", 0)

        # Compute health score (same as in report_builder)
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

        if await ollama.is_available():
            prompt = build_analysis_prompt(
                repo_name=meta.get("full_name", f"{owner}/{repo}"),
                description=meta.get("description") or "",
                languages={},           # Already percentage-converted in report_builder
                total_commits=len(raw_data.get("commits", [])),
                total_contributors=len(raw_data.get("contributors", [])),
                stars=stars,
                forks=forks,
                open_issues=issues,
                last_commit_days_ago=_last_commit_days(raw_data.get("commits", [])),
                health_score=health_score,
                contributor_summaries=contributor_summaries,
                hourly_distribution=patterns_result.hourly_distribution,
                daily_distribution=patterns_result.daily_distribution,
            )
            raw_llm = await ollama.generate(prompt)
            if raw_llm:
                llm_insights = parse_llm_response(raw_llm, ollama.model)
                if llm_insights:
                    logger.info("LLM insights generated successfully.")
                else:
                    logger.warning("LLM response could not be parsed — using fallback.")

        if llm_insights is None:
            logger.info("Using heuristic fallback insights (Ollama unavailable or parse failed).")
            fallback = build_fallback_insights(
                repo_name=meta.get("full_name", f"{owner}/{repo}"),
                total_contributors=len(raw_data.get("contributors", [])),
                health_score=health_score,
                contributor_summaries=contributor_summaries,
            )
            llm_insights = insights_from_fallback(fallback)

        # ── Phase 4: Report Assembly ──────────────────────────
        logger.info("Building final report...")
        report = build_report(raw_data, analytics_result, llm_insights)
        report.patterns = patterns_result

        # Cache the result for 15 minutes
        cache.set(cache_key, report, ttl_seconds=900)

        return report

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Check backend health and Ollama availability."""
    import datetime
    ollama = OllamaClient()
    ollama_up = await ollama.is_available()
    return {
        "status": "ok",
        "server": "RepoIntel Backend",
        "timestamp": datetime.datetime.now().isoformat(),
        "ollama": {
            "available": ollama_up,
            "url": ollama.base_url,
            "model": ollama.model,
        },
    }


@router.get("/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Check the status of a background analysis task (future async support)."""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return analysis_store[analysis_id]


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _last_commit_days(commits: list) -> int:
    """Return how many days ago the most recent commit was made."""
    from datetime import datetime, timezone
    if not commits:
        return 0
    date_str = commits[0].get("commit", {}).get("author", {}).get("date")
    if not date_str:
        return 0
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).days
    except ValueError:
        return 0
