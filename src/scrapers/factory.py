"""
src/scrapers/factory.py

Factory and registry for all scrapers.
Every scraper is registered here with display metadata for the CLI.

Author : M-D (Mohamed Darwish)
"""

from dataclasses import dataclass
from typing import Optional

from src.scrapers.base import BaseScraper, ScraperConfig
from src.scrapers.simulated import (
    AmazonScraper, NoonScraper, AliExpressScraper,
    JumiaScraper, EbayScraper,
)
from src.scrapers.custom_sites import (
    load_custom_sites, save_custom_site, CustomSiteData
)
from src.utils.http_client import HttpClient
from src.utils.logger import get_logger


logger = get_logger(__name__)


@dataclass
class SiteInfo:
    name:        str
    description: str
    currency:    str
    mode:        str    # "live" or "simulated"
    scraper_cls: type[BaseScraper]


# Global registry instance to allow dynamic updates
REGISTRY: dict[str, SiteInfo] = {
    "amazon": SiteInfo(
        name        = "Amazon",
        description = "Global marketplace — electronics, fashion, books, and more",
        currency    = "USD",
        mode        = "simulated",
        scraper_cls = AmazonScraper,
    ),
    "noon": SiteInfo(
        name        = "Noon",
        description = "Leading MENA e-commerce platform",
        currency    = "AED",
        mode        = "simulated",
        scraper_cls = NoonScraper,
    ),
    "aliexpress": SiteInfo(
        name        = "AliExpress",
        description = "Global wholesale marketplace with wide variety",
        currency    = "USD",
        mode        = "simulated",
        scraper_cls = AliExpressScraper,
    ),
    "jumia": SiteInfo(
        name        = "Jumia",
        description = "Africa's largest e-commerce platform",
        currency    = "EGP",
        mode        = "simulated",
        scraper_cls = JumiaScraper,
    ),
    "ebay": SiteInfo(
        name        = "eBay",
        description = "Consumer-to-consumer and retail auction platform",
        currency    = "USD",
        mode        = "simulated",
        scraper_cls = EbayScraper,
    ),
}


def load_saved_custom_sites() -> None:
    """
    Load custom sites that were previously added by users.
    This is called automatically at startup to restore user-added sites.
    Sites are saved to data/custom_sites.json and persist across restarts.
    """
    custom = load_custom_sites()
    for key, site_data in custom.items():
        REGISTRY[key] = SiteInfo(
            name        = site_data.name,
            description = f"Custom: {site_data.url}",
            currency    = site_data.currency,
            mode        = "simulated",
            scraper_cls = AmazonScraper,
        )
    if custom:
        logger.info(f"Loaded {len(custom)} custom sites from disk")


def add_custom_site(name: str, url: str, currency: str = "USD") -> str:
    """Dynamically register a new e-commerce site and save it."""
    key = name.lower().replace(" ", "_")
    
    REGISTRY[key] = SiteInfo(
        name        = name,
        description = f"Custom site: {url}",
        currency    = currency,
        mode        = "simulated",
        scraper_cls = AmazonScraper,
    )
    
    # Save to disk so it persists
    save_custom_site(key, CustomSiteData(name=name, url=url, currency=currency))
    
    return key


def create_scraper(
    key:         str,
    config:      Optional[ScraperConfig] = None,
    http_client: Optional[HttpClient]    = None,
) -> BaseScraper:
    """
    Instantiate a scraper by its registered key.

    Raises ValueError for unknown keys.
    """
    k = key.lower().strip()
    if k not in REGISTRY:
        available = ", ".join(sorted(REGISTRY.keys()))
        raise ValueError(f"Unknown site '{key}'. Available: {available}")

    info   = REGISTRY[k]
    cfg    = config or ScraperConfig()
    client = http_client or HttpClient(
        delay_min   = cfg.delay_min,
        delay_max   = cfg.delay_max,
        timeout     = cfg.timeout,
        max_retries = cfg.max_retries,
    )
    logger.info(f"Creating {info.scraper_cls.__name__} ({info.mode})")
    return info.scraper_cls(config=cfg, http_client=client)


def list_sites() -> list[tuple[str, SiteInfo]]:
    """Return all registered sites as (key, SiteInfo) pairs."""
    return list(REGISTRY.items())


def site_keys() -> list[str]:
    return list(REGISTRY.keys())
