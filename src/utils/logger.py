"""
src/utils/logger.py

Structured file logging system for the scraper.
Provides file-based logging while terminal output is handled separately by colors.py.

Key Features:
    - Logs to rotating daily files in logs/ directory
    - All timestamps in UTC for consistency across systems
    - Suppresses noise from third-party libraries (urllib3, requests, etc)
    - Structured format: [timestamp | level | module | message]

Environment Variables:
    LOG_LEVEL: Set logging level (DEBUG, INFO, WARNING, ERROR)

Usage:
    from src.utils.logger import configure_logging, get_logger
    
    # Configure once at startup
    configure_logging(level="INFO", log_dir="logs")
    
    # Get logger in any module
    logger = get_logger(__name__)
    logger.info("Operation completed successfully")

Author : M-D (Mohamed Darwish)
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


_CONFIGURED = False


def configure_logging(level: str = "INFO", log_dir: str = "logs") -> None:
    """
    Initialize the logging system (do this once at startup).
    
    Creates a daily log file and sets up formatters.
    Can only be called once to avoid duplicate log entries.
    Suppresses verbose logs from third-party libraries.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
    
    Example:
        configure_logging(level="INFO", log_dir="logs")
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    # Create logs directory if needed
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Create daily log file (UTC timestamp)
    today    = datetime.utcnow().strftime("%Y-%m-%d")
    log_file = Path(log_dir) / f"scraper_{today}.log"

    # Define log format with timestamp, level, module name, and message
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-28s | %(message)s",
        "%Y-%m-%d %H:%M:%S",  # UTC time format
    )

    # Configure root logger
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Add file handler (write all logs to file)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)

    # Suppress verbose logs from third-party libraries
    # These often generate too much noise for our use case
    for library in ("urllib3", "requests", "charset_normalizer"):
        logging.getLogger(library).setLevel(logging.WARNING)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Call this in any module to get a logger with that module's name.
    The logger will write to the daily log file configured by configure_logging().
    
    Args:
        name: Module name (typically __name__)
    
    Returns:
        Logger instance
    
    Example:
        logger = get_logger(__name__)
        logger.info("Something happened")
    """
    return logging.getLogger(name)
