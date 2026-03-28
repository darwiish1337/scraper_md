"""
src/scrapers/base.py

Abstract base class — defines the contract every scraper must fulfil.
Adding a new site = subclassing this, zero changes here.

Author : M-D (Mohamed Darwish)
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from src.models.product import Product, ScrapeResult, ScraperSource
from src.utils.http_client import HttpClient
from src.utils.logger import get_logger


@dataclass
class ScraperConfig:
    max_pages:   int   = 5
    delay_min:   float = 1.5
    delay_max:   float = 4.0
    timeout:     int   = 30
    max_retries: int   = 3


class BaseScraper(ABC):
    """
    Contract for all e-commerce scrapers.

    Subclasses must implement:
        source, base_url, search_products, get_product, _parse_product
    """

    def __init__(self, config: ScraperConfig, http_client: HttpClient):
        self.config = config
        self.http   = http_client
        self.logger = get_logger(self.__class__.__name__)
        self._t0:   float = 0.0

    @property
    @abstractmethod
    def source(self) -> ScraperSource: ...

    @property
    @abstractmethod
    def base_url(self) -> str: ...

    @abstractmethod
    def search_products(
        self,
        query:      str,
        max_pages:  Optional[int] = None,
        category:   Optional[str] = None,
    ) -> ScrapeResult: ...

    @abstractmethod
    def get_product(self, url: str) -> Optional[Product]: ...

    @abstractmethod
    def _parse_product(self, raw: dict) -> Optional[Product]: ...

    def _start(self) -> None:
        self._t0 = time.time()

    def _elapsed(self) -> float:
        return round(time.time() - self._t0, 2)

    def _build_result(
        self,
        products: list[Product],
        errors:   list[str],
        pages:    int,
    ) -> ScrapeResult:
        return ScrapeResult(
            success          = len(products) > 0,
            products         = products,
            errors           = errors,
            pages_scraped    = pages,
            duration_seconds = self._elapsed(),
            source           = self.source,
        )
