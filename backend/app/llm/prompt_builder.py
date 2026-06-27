"""
Prompt builder for the LLM orchestrator.

Constructs a structured prompt that asks Ollama to analyze the repository
and return a JSON object with all required insight fields.

Design principles:
- Low temperature prompting: explicit JSON schema in the prompt
- Few-shot example: one example output to guide the model
- Concise data: only send meaningful stats, not raw API dumps
"""

import json
from typing import List, Dict, Any


def build_analysis_prompt(
    repo_name: str,
    description: str,
    languages: Dict[str, float],
    total_commits: int,
    total_contributors: int,
    stars: int,
    forks: int,
    open_issues: int,
    last_commit_days_ago: int,
    health_score: float,
    contributor_summaries: List[Dict[str, Any]],
    hourly_distribution: List[int],
    daily_distribution: List[int],
) -> str:
    """
    Build the full analysis prompt to send to Ollama.

    Args:
        All pre-computed analytics data needed for the prompt.

    Returns:
        A formatted string prompt ready to be sent to Ollama.
    """

    # Format language breakdown
    top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
    lang_str = ", ".join(f"{lang} ({pct:.1f}%)" for lang, pct in top_langs)

    # Format contributor summaries (top 6 only for token budget)
    top_contributors = contributor_summaries[:6]
    contrib_lines = []
    for c in top_contributors:
        line = (
            f"  - {c['username']}: {c['commits']} commits, "
            f"quality_score={c['commit_quality_score']}/100, "
            f"personality={c['personality']}, "
            f"ai_likelihood={c['ai_code_likelihood']}%, "
            f"pattern={c['contribution_pattern']}, "
            f"risk={c['risk_level']}"
        )
        contrib_lines.append(line)
    contrib_str = "\n".join(contrib_lines)

    # Derive peak activity from distributions
    peak_hour = hourly_distribution.index(max(hourly_distribution)) if hourly_distribution else 14
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    peak_day = days[daily_distribution.index(max(daily_distribution))] if daily_distribution else "Wednesday"

    prompt = f"""You are an expert software engineering analyst. Analyze the following GitHub repository data and provide a structured JSON report.

## Repository: {repo_name}
Description: {description or "No description provided."}
Languages: {lang_str}
Stars: {stars:,} | Forks: {forks:,} | Open Issues: {open_issues:,}
Total Commits (sampled): {total_commits} | Total Contributors: {total_contributors}
Last commit: {last_commit_days_ago} days ago
Health Score (heuristic): {health_score:.0f}/100

## Contributor Analysis
{contrib_str}

## Contribution Patterns
- Peak coding hour: {peak_hour}:00 UTC
- Most active day: {peak_day}

## Task
Analyze the above data and return ONLY a valid JSON object. Do not include any explanation, markdown formatting, or code fences. Return only the raw JSON.

The JSON must have EXACTLY these keys:
{{
  "project_explanation": "<2-3 sentence beginner-friendly explanation of what this project does and its significance>",
  "team_behavior": "<2-3 sentences describing the team's development style, collaboration patterns, and work habits>",
  "overall_health": "<one of: excellent, good, fair, poor>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>"],
  "risks": ["<risk 1>", "<risk 2>"],
  "recommendations": [
    {{
      "type": "<one of: positive, warning, critical, general>",
      "target": "<contributor username or 'team'>",
      "title": "<short action title>",
      "detail": "<2 sentence detail explaining why and what to do>"
    }}
  ]
}}

Rules:
- overall_health must be exactly one of: excellent, good, fair, poor
- strengths, weaknesses, risks: each list must have 2–5 items
- recommendations: 2–5 items, mixing types (positive, warning, critical, general)
- All text must be in plain English, beginner-friendly but accurate
- Do not mention that you are an AI or that this is generated content

Return ONLY the JSON object. Nothing else."""

    return prompt


def build_fallback_insights(
    repo_name: str,
    total_contributors: int,
    health_score: float,
    contributor_summaries: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build template-based insights when Ollama is unavailable.
    These are heuristic-derived, not AI-generated.

    Returns a dict matching the LLMInsights structure.
    """
    health_label = (
        "excellent" if health_score >= 80
        else "good" if health_score >= 60
        else "fair" if health_score >= 40
        else "poor"
    )

    top_contributor = contributor_summaries[0]["username"] if contributor_summaries else "the team"
    high_risk = [c for c in contributor_summaries if c.get("risk_level") == "high"]
    low_quality = [c for c in contributor_summaries if c.get("commit_quality_score", 100) < 50]

    strengths = [
        f"Active repository with {total_contributors} contributors",
        "Commit history available for analysis",
    ]
    weaknesses = ["AI-powered insights unavailable (Ollama not running)"]
    risks = []

    if high_risk:
        risks.append(f"{len(high_risk)} contributor(s) flagged as high risk based on commit patterns")
    if low_quality:
        risks.append(f"{len(low_quality)} contributor(s) have low commit message quality scores")

    recommendations = [
        {
            "type": "general",
            "target": "team",
            "title": "Install Ollama for AI Insights",
            "detail": (
                "Run 'ollama serve' and 'ollama pull llama3.2:3b' to enable AI-powered analysis. "
                "Without it, insights are heuristic-based only."
            )
        }
    ]

    if contributor_summaries:
        recommendations.append({
            "type": "positive",
            "target": top_contributor,
            "title": "Leading Contributor",
            "detail": (
                f"{top_contributor} has the highest commit count in this repository. "
                "Continue maintaining high contribution levels."
            )
        })

    return {
        "project_explanation": (
            f"{repo_name} is a GitHub repository with {total_contributors} contributors "
            f"and a health score of {health_score:.0f}/100 based on heuristic analysis. "
            "Install Ollama to get a detailed AI-powered explanation of this project."
        ),
        "team_behavior": (
            f"The team has {total_contributors} active contributors. "
            "Detailed team behavior analysis requires Ollama to be running locally."
        ),
        "overall_health": health_label,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "risks": risks if risks else ["No critical risks identified from heuristic analysis"],
        "recommendations": recommendations,
    }
