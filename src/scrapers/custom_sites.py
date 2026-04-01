"""
src/scrapers/custom_sites.py

Manage custom/user-added e-commerce sites.
Persists custom sites to disk so they survive app restarts.
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict

from src.utils.logger import get_logger

logger = get_logger(__name__)

# File to store custom sites
CUSTOM_SITES_FILE = Path(__file__).parent.parent.parent / "data" / "custom_sites.json"


@dataclass
class CustomSiteData:
    """Data structure for a custom site."""
    name: str
    url: str
    currency: str


def load_custom_sites() -> dict[str, CustomSiteData]:
    """
    Load custom sites from disk.
    Returns empty dict if file doesn't exist or is invalid.
    """
    if not CUSTOM_SITES_FILE.exists():
        return {}
    
    try:
        with open(CUSTOM_SITES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert dict back to CustomSiteData objects
        sites = {
            key: CustomSiteData(**value)
            for key, value in data.items()
        }
        logger.info(f"Loaded {len(sites)} custom sites from disk")
        return sites
    except Exception as e:
        logger.error(f"Failed to load custom sites: {e}")
        return {}


def save_custom_site(key: str, site: CustomSiteData) -> None:
    """
    Save a custom site to disk.
    Updates existing site if key already exists.
    """
    CUSTOM_SITES_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing sites
    existing = load_custom_sites()
    
    # Add or update
    existing[key] = site
    
    # Save to file
    try:
        with open(CUSTOM_SITES_FILE, 'w', encoding='utf-8') as f:
            # Convert to plain dicts for JSON serialization
            json.dump(
                {k: asdict(v) for k, v in existing.items()},
                f,
                indent=2,
                ensure_ascii=False
            )
        logger.info(f"Saved custom site: {key}")
    except Exception as e:
        logger.error(f"Failed to save custom site: {e}")


def remove_custom_site(key: str) -> None:
    """Remove a custom site from disk."""
    existing = load_custom_sites()
    if key in existing:
        del existing[key]
        try:
            with open(CUSTOM_SITES_FILE, 'w', encoding='utf-8') as f:
                json.dump(
                    {k: asdict(v) for k, v in existing.items()},
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            logger.info(f"Removed custom site: {key}")
        except Exception as e:
            logger.error(f"Failed to remove custom site: {e}")
