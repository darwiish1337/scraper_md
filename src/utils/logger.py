"""
src/utils/logger.py

Structured file logging. Terminal output is handled by colors.py only.
The logger writes to logs/ and is silent on stdout by default.

Author : M-D (Mohamed Darwish)
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


_CONFIGURED = False


def configure_logging(level: str = "INFO", log_dir: str = "logs") -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    Path(log_dir).mkdir(parents=True, exist_ok=True)
    today    = datetime.utcnow().strftime("%Y-%m-%d")
    log_file = Path(log_dir) / f"scraper_{today}.log"

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-28s | %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)

    for noisy in ("urllib3", "requests", "charset_normalizer"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
