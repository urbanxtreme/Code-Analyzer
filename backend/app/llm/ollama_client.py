"""
Async HTTP client for communicating with a local Ollama instance.

Handles:
- Sending prompts to Ollama's /api/generate endpoint
- Health-checking Ollama availability
- Graceful degradation (returns None if Ollama is unreachable)
- Timeout + single retry logic
"""

import httpx
import json
import logging
from typing import Optional

from ..utils.config import settings

logger = logging.getLogger(__name__)

OLLAMA_TIMEOUT = 120.0  # seconds — LLM inference can be slow on CPU


class OllamaClient:
    """Async HTTP client for the Ollama local LLM API."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    async def is_available(self) -> bool:
        """
        Ping Ollama to check if it is running.
        Returns True if the server responds, False otherwise.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def generate(self, prompt: str, retry: bool = True) -> Optional[str]:
        """
        Send a prompt to Ollama and return the raw response text.

        Args:
            prompt: The full prompt string to send.
            retry: If True, retry once with a simpler prompt on failure.

        Returns:
            The LLM's response string, or None if Ollama is unavailable.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,   # Low temperature = more consistent JSON output
                "num_predict": 1500,  # Max tokens in response
            }
        }

        try:
            async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
                logger.info(f"Sending prompt to Ollama model '{self.model}' ({len(prompt)} chars)...")
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                resp.raise_for_status()
                data = resp.json()
                raw_text = data.get("response", "").strip()
                logger.info(f"Ollama responded with {len(raw_text)} chars.")
                return raw_text

        except httpx.ConnectError:
            logger.warning("Ollama is not running or not reachable at %s.", self.base_url)
            return None

        except httpx.TimeoutException:
            logger.warning("Ollama request timed out after %.0fs.", OLLAMA_TIMEOUT)
            if retry:
                # Retry with a shorter, simpler prompt
                logger.info("Retrying with a condensed prompt...")
                short_prompt = _condense_prompt(prompt)
                return await self.generate(short_prompt, retry=False)
            return None

        except Exception as e:
            logger.error("Unexpected Ollama error: %s", str(e))
            return None


def _condense_prompt(prompt: str) -> str:
    """
    Shorten a prompt when retrying after a timeout.
    Keeps the system instructions and truncates the data section.
    """
    lines = prompt.split("\n")
    # Keep first 40 lines (system instructions + some data) and append the closing request
    condensed = "\n".join(lines[:40])
    condensed += "\n\nBased on the above limited data, provide your best JSON analysis.\n"
    return condensed
