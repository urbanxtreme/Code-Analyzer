from typing import List, Dict, Any
from datetime import datetime, timezone
import collections
from ..api.schemas import Patterns

def detect_patterns(raw_commits: List[Dict[str, Any]]) -> Patterns:
    """Detects hourly, daily, and monthly contribution patterns from commits."""
    
    hourly = [0] * 24
    daily = [0] * 7  # 0 is Monday, 6 is Sunday
    monthly_data = collections.defaultdict(int)
    
    # Use the last 12 months for labels
    labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_counts = [0] * 12

    for commit in raw_commits:
        commit_date_str = commit.get("commit", {}).get("author", {}).get("date")
        if not commit_date_str:
            continue
            
        dt = datetime.strptime(commit_date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        
        # Hourly (0-23)
        hourly[dt.hour] += 1
        
        # Daily (0-6)
        daily[dt.weekday()] += 1
        
        # Monthly
        monthly_counts[dt.month - 1] += 1

    return Patterns(
        hourly_distribution=hourly,
        daily_distribution=daily,
        commit_frequency={
            "labels": labels,
            "data": monthly_counts
        }
    )
