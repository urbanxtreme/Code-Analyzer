import logging
import sys
from .config import settings


def setup_logging():
    """Configure root logging for the entire application."""
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )
    # Quiet noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


# Convenience alias kept for backward compatibility
def setup_logger():
    setup_logging()
    return logging.getLogger("repo-intel")


logger = logging.getLogger("repo-intel")
