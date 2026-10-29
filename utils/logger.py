"""
utils/logger.py – Application-wide logging setup.
Sensitive fields (API keys) are never written to logs.
"""

import logging
import sys
from config import LOG_LEVEL


def setup_logging() -> None:
    """Configure root logger with a clean formatter."""
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    logging.basicConfig(
        level=level,
        format=fmt,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Suppress noisy third-party loggers
    for noisy in ("urllib3", "httpx", "httpcore", "ibm_watsonx_ai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
