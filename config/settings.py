"""
config/settings.py

Central configuration management for the M-D Web Scraper.
All settings are derived from environment variables with sensible defaults,
allowing for easy customization without code changes.

Environment Variables:
    - SCRAPER_MAX_PAGES: Maximum pages to scrape per site (default: 5)
    - SCRAPER_DELAY_MIN: Minimum delay between requests in seconds (default: 1.5)
    - SCRAPER_DELAY_MAX: Maximum delay between requests in seconds (default: 4.0)
    - SCRAPER_TIMEOUT: Request timeout in seconds (default: 30)
    - SCRAPER_MAX_RETRIES: Maximum retry attempts on failure (default: 3)
    - LOG_LEVEL: Logging level - DEBUG, INFO, WARNING, ERROR (default: INFO)

Example:
    # In terminal before running
    export SCRAPER_MAX_PAGES=10
    export LOG_LEVEL=DEBUG
    python main.py

Author : M-D (Mohamed Darwish)
"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    """
    Application settings with validation and defaults.
    All paths are relative to project root for portability.
    """
    
    # --- Project structure ---
    project_root:  Path = Path(__file__).parent.parent
    data_dir:      Path = Path(__file__).parent.parent / "data"
    processed_dir: Path = Path(__file__).parent.parent / "data" / "processed"
    logs_dir:      Path = Path(__file__).parent.parent / "logs"
    db_path:       str  = str(Path(__file__).parent.parent / "data" / "scraper.db")

    # --- Scraper behavior ---
    # Maximum number of pages to scrape per site
    max_pages:   int   = int(os.environ.get("SCRAPER_MAX_PAGES",   "5"))
    
    # Minimum delay between requests (in seconds)
    # Prevents overwhelming target servers and helps avoid rate limiting
    delay_min:   float = float(os.environ.get("SCRAPER_DELAY_MIN", "1.5"))
    
    # Maximum delay between requests (in seconds)
    # Random delays between min and max are used for realistic behavior
    delay_max:   float = float(os.environ.get("SCRAPER_DELAY_MAX", "4.0"))
    
    # Request timeout in seconds
    # Prevents hanging on unresponsive servers
    timeout:     int   = int(os.environ.get("SCRAPER_TIMEOUT",     "30"))
    
    # Maximum number of retry attempts on request failure
    # Improves reliability on flaky connections
    max_retries: int   = int(os.environ.get("SCRAPER_MAX_RETRIES", "3"))
    
    # --- Logging ---
    # Available levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_level:   str   = os.environ.get("LOG_LEVEL", "INFO")

    def __post_init__(self) -> None:
        """
        Create required directories on initialization.
        Ensures data_dir, processed_dir, and logs_dir exist.
        """
        for directory in [self.data_dir, self.processed_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> None:
        """
        Validate settings are within acceptable ranges.
        Raises ValueError if any setting is invalid.
        """
        if self.max_pages < 1 or self.max_pages > 500:
            raise ValueError(f"max_pages must be between 1 and 500, got {self.max_pages}")
        
        if self.delay_min < 0 or self.delay_max < 0:
            raise ValueError("Delays cannot be negative")
        
        if self.delay_min > self.delay_max:
            raise ValueError(f"delay_min ({self.delay_min}) > delay_max ({self.delay_max})")
        
        if self.timeout < 1 or self.timeout > 300:
            raise ValueError(f"timeout must be between 1 and 300, got {self.timeout}")
        
        if self.max_retries < 0 or self.max_retries > 10:
            raise ValueError(f"max_retries must be between 0 and 10, got {self.max_retries}")
        
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")


# Global settings instance - initialized on module load
settings = Settings()
settings.validate()
