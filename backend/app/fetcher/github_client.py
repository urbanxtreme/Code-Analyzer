import httpx
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from ..api.schemas import RepositoryMetadata, ContributorStats
from datetime import datetime

load_dotenv()

class GitHubClient:
    """Async HTTP client for interacting with the GitHub REST API."""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Repo-Analyzer"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    async def fetch_repository_data(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetches all necessary repository data from GitHub."""
        async with httpx.AsyncClient(headers=self.headers, base_url=self.base_url, timeout=30.0) as client:
            # 1. Fetch Repository Metadata
            meta_resp = await client.get(f"/repos/{owner}/{repo}")
            if meta_resp.status_code != 200:
                raise Exception(f"Failed to fetch repository metadata: {meta_resp.text}")
            meta = meta_resp.json()

            # 2. Fetch Languages
            lang_resp = await client.get(f"/repos/{owner}/{repo}/languages")
            languages = lang_resp.json() if lang_resp.status_code == 200 else {}

            # 3. Fetch Contributors
            cont_resp = await client.get(f"/repos/{owner}/{repo}/contributors")
            contributors = cont_resp.json() if cont_resp.status_code == 200 else []

            # 4. Fetch Commits (last 100)
            commit_resp = await client.get(f"/repos/{owner}/{repo}/commits?per_page=100")
            commits = commit_resp.json() if commit_resp.status_code == 200 else []

            # 5. Fetch File Tree (recursive) to analyze project structure
            tree_resp = await client.get(f"/repos/{owner}/{repo}/git/trees/{meta['default_branch']}?recursive=1")
            tree = tree_resp.json().get("tree", []) if tree_resp.status_code == 200 else []

            return {
                "metadata": meta,
                "languages": languages,
                "contributors": contributors,
                "commits": commits,
                "tree": tree
            }
