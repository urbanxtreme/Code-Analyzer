import logging
import sys
from .config import settings

def setup_logger():
    """Configures the application logger."""
    logger = logging.getLogger("repo-intel")
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

logger = setup_logger()
