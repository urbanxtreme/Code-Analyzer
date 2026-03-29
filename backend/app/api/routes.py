from fastapi import APIRouter, HTTPException, BackgroundTasks
from .schemas import AnalysisRequest, FinalReport
from ..fetcher.github_client import GitHubClient
from ..analytics.contributor_analyzer import analyze_contributors
from ..analytics.pattern_detector import detect_patterns
from ..report.report_builder import build_report
import uuid
import datetime

router = APIRouter()

# In-memory store for analysis status (in production, use a database/Redis)
analysis_store = {}

@router.post("/analyze", response_model=FinalReport)
async def analyze_repository(request: AnalysisRequest):
    """
    Synchronous analysis of a repository.
    Fetches data from GitHub, performs analysis, and returns the report.
    """
    try:
        # Extract owner and repo from URL
        # For MVP, we'll assume a standard URL or owner/repo shorthand.
        parts = request.repo_url.strip("/").split("/")
        if len(parts) < 2:
            raise HTTPException(status_code=400, detail="Invalid repository URL format. Use 'owner/repo' or full GitHub URL.")
        
        owner, repo = parts[-2], parts[-1]
        
        # Phase 1: Data Collection
        client = GitHubClient()
        raw_data = await client.fetch_repository_data(owner, repo)
        
        # Phase 2: Analysis (Basic for Phase 1)
        analytics_result = analyze_contributors(raw_data)
        patterns_result = detect_patterns(raw_data.get("commits", []))
        
        # Phase 3: AI Insights (Mocked for Phase 1 until Ollama is hooked up)
        # Phase 4: Report Assembly
        report = build_report(raw_data, analytics_result, insights=None)
        
        # Override the patterns with actual results
        report.patterns = patterns_result
        
        return report

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Check the status of a background analysis task."""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return analysis_store[analysis_id]
