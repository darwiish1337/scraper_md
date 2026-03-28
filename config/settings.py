"""
config/settings.py

Central configuration. Override via environment variables.

Author : M-D (Mohamed Darwish)
"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    project_root:  Path = Path(__file__).parent.parent
    data_dir:      Path = Path(__file__).parent.parent / "data"
    processed_dir: Path = Path(__file__).parent.parent / "data" / "processed"
    logs_dir:      Path = Path(__file__).parent.parent / "logs"
    db_path:       str  = str(Path(__file__).parent.parent / "data" / "scraper.db")

    max_pages:   int   = int(os.environ.get("SCRAPER_MAX_PAGES",   "5"))
    delay_min:   float = float(os.environ.get("SCRAPER_DELAY_MIN", "1.5"))
    delay_max:   float = float(os.environ.get("SCRAPER_DELAY_MAX", "4.0"))
    timeout:     int   = int(os.environ.get("SCRAPER_TIMEOUT",     "30"))
    max_retries: int   = int(os.environ.get("SCRAPER_MAX_RETRIES", "3"))
    log_level:   str   = os.environ.get("LOG_LEVEL", "INFO")

    def __post_init__(self):
        for d in [self.data_dir, self.processed_dir, self.logs_dir]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
