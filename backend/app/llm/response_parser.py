"""
LLM response parser for Ollama output.

Handles:
- Stripping markdown code fences (```json ... ```) that the model may wrap output in
- Parsing JSON from the LLM response
- Validating the parsed JSON has all required keys
- Returning a typed LLMInsights object
"""

import json
import re
import logging
from typing import Optional, Dict, Any

from .models import LLMInsights, LLMRecommendation

logger = logging.getLogger(__name__)

REQUIRED_KEYS = {
    "project_explanation",
    "team_behavior",
    "overall_health",
    "strengths",
    "weaknesses",
    "risks",
    "recommendations",
}

VALID_HEALTH_VALUES = {"excellent", "good", "fair", "poor"}
VALID_REC_TYPES = {"positive", "warning", "critical", "general"}


def parse_llm_response(raw_text: str, model_name: str) -> Optional[LLMInsights]:
    """
    Parse and validate the raw LLM text response into a LLMInsights object.

    Args:
        raw_text: The raw string returned by Ollama.
        model_name: Name of the model used (for metadata).

    Returns:
        LLMInsights on success, None on failure.
    """
    if not raw_text:
        logger.warning("Received empty response from Ollama.")
        return None

    # Step 1: Strip markdown code fences if present
    cleaned = _strip_code_fences(raw_text)

    # Step 2: Extract first JSON object from the text
    json_str = _extract_json(cleaned)
    if not json_str:
        logger.warning("Could not find JSON object in Ollama response.")
        logger.debug("Raw response was: %s", raw_text[:500])
        return None

    # Step 3: Parse JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning("JSON decode error: %s. Attempting repair...", str(e))
        data = _attempt_json_repair(json_str)
        if data is None:
            return None

    # Step 4: Validate required keys
    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        logger.warning("LLM response missing keys: %s", missing)
        # Fill in defaults for missing keys
        data = _fill_defaults(data)

    # Step 5: Sanitize and build model
    try:
        return _build_insights(data, model_name)
    except Exception as e:
        logger.error("Failed to build LLMInsights: %s", str(e))
        return None


def insights_from_fallback(fallback_dict: Dict[str, Any]) -> LLMInsights:
    """
    Convert a fallback dict (from prompt_builder.build_fallback_insights) into
    a LLMInsights object with llm_available=False.
    """
    recommendations = [
        LLMRecommendation(
            type=r.get("type", "general"),
            target=r.get("target", "team"),
            title=r.get("title", "Recommendation"),
            detail=r.get("detail", ""),
        )
        for r in fallback_dict.get("recommendations", [])
    ]

    return LLMInsights(
        project_explanation=fallback_dict["project_explanation"],
        team_behavior=fallback_dict["team_behavior"],
        overall_health=fallback_dict.get("overall_health", "fair"),
        strengths=fallback_dict.get("strengths", []),
        weaknesses=fallback_dict.get("weaknesses", []),
        risks=fallback_dict.get("risks", []),
        recommendations=recommendations,
        llm_available=False,
        model_used=None,
    )


# ──────────────────────────────────────────────────────────────
# Private helpers
# ──────────────────────────────────────────────────────────────

def _strip_code_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers."""
    # Match ```json\n...\n``` or ```\n...\n```
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return text.strip()


def _extract_json(text: str) -> Optional[str]:
    """
    Find the first complete JSON object {...} in the text.
    Handles cases where the model adds extra prose before/after the JSON.
    """
    # Try to find the outermost { ... }
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    for i, ch in enumerate(text[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    return None


def _attempt_json_repair(json_str: str) -> Optional[Dict]:
    """
    Try simple repairs on malformed JSON:
    - Remove trailing commas before } or ]
    - Handle single quotes instead of double quotes
    """
    try:
        # Remove trailing commas
        repaired = re.sub(r",\s*([}\]])", r"\1", json_str)
        return json.loads(repaired)
    except Exception:
        pass

    try:
        # Try replacing single quotes with double (very naive, but helps sometimes)
        repaired = json_str.replace("'", '"')
        return json.loads(repaired)
    except Exception:
        return None


def _fill_defaults(data: Dict) -> Dict:
    """Fill in missing required keys with sensible defaults."""
    defaults = {
        "project_explanation": "This repository was analyzed but a detailed explanation could not be generated.",
        "team_behavior": "Team behavior analysis was not available.",
        "overall_health": "fair",
        "strengths": ["Repository has commit history available for analysis"],
        "weaknesses": ["Detailed analysis was incomplete"],
        "risks": ["Manual review recommended"],
        "recommendations": [],
    }
    for key, value in defaults.items():
        if key not in data:
            data[key] = value
    return data


def _build_insights(data: Dict, model_name: str) -> LLMInsights:
    """Construct and validate the final LLMInsights object."""

    # Sanitize overall_health
    health = str(data.get("overall_health", "fair")).lower().strip()
    if health not in VALID_HEALTH_VALUES:
        health = "fair"

    # Sanitize list fields
    strengths = _ensure_str_list(data.get("strengths", []))[:5]
    weaknesses = _ensure_str_list(data.get("weaknesses", []))[:5]
    risks = _ensure_str_list(data.get("risks", []))[:5]

    # Sanitize recommendations
    raw_recs = data.get("recommendations", [])
    recommendations = []
    for r in raw_recs[:5]:
        if not isinstance(r, dict):
            continue
        rec_type = str(r.get("type", "general")).lower()
        if rec_type not in VALID_REC_TYPES:
            rec_type = "general"
        recommendations.append(
            LLMRecommendation(
                type=rec_type,
                target=str(r.get("target", "team")),
                title=str(r.get("title", "Recommendation")),
                detail=str(r.get("detail", "")),
            )
        )

    return LLMInsights(
        project_explanation=str(data.get("project_explanation", "")),
        team_behavior=str(data.get("team_behavior", "")),
        overall_health=health,
        strengths=strengths,
        weaknesses=weaknesses,
        risks=risks,
        recommendations=recommendations,
        llm_available=True,
        model_used=model_name,
    )


def _ensure_str_list(value) -> list:
    """Ensure a value is a list of strings."""
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if isinstance(value, str):
        return [value]
    return []
