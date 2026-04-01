"""
src/scrapers/base.py

Abstract base class defining the contract for all e-commerce scrapers.
Ensures all scrapers follow the same interface and lifecycle.

Key Concepts:
    - Every scraper must inherit from BaseScraper
    - Subclasses implement site-specific parsing logic
    - Common functionality like timing and result formatting is in the base
    - Adding a new site requires only subclassing - no changes to this file

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
    """
    Configuration settings for scraper behavior.
    
    Attributes:
        max_pages: Maximum number of pages to scrape per search
        delay_min: Minimum random delay between requests (seconds)
        delay_max: Maximum random delay between requests (seconds)
        timeout: HTTP request timeout (seconds)
        max_retries: Number of retry attempts for failed requests
    
    Example:
        config = ScraperConfig(max_pages=10, delay_min=2.0, delay_max=5.0)
    """
    max_pages:   int   = 5
    delay_min:   float = 1.5
    delay_max:   float = 4.0
    timeout:     int   = 30
    max_retries: int   = 3


class BaseScraper(ABC):
    """
    Abstract base class for all e-commerce scrapers.
    
    Defines the interface that all scrapers must implement:
        - source: Enum identifying the e-commerce platform
        - base_url: Root URL of the platform
        - search_products(): Main scraping method
        - get_product(): Fetch single product details
        - _parse_product(): Parse raw product data
    
    Includes common functionality:
        - Timing and duration tracking
        - Result building with metadata
        - Logging for debugging
    
    Usage:
        class AmazonScraper(BaseScraper):
            @property
            def source(self) -> ScraperSource:
                return ScraperSource.AMAZON
            
            def search_products(self, query, max_pages, category):
                # Site-specific implementation
                pass
    """

    def __init__(self, config: ScraperConfig, http_client: HttpClient):
        """
        Initialize scraper with configuration and HTTP client.
        
        Args:
            config: ScraperConfig instance with timing and retry settings
            http_client: HttpClient for making HTTP requests
        """
        self.config = config
        self.http   = http_client
        self.logger = get_logger(self.__class__.__name__)
        self._t0:   float = 0.0  # Start time for duration tracking

    # --- Abstract properties - must be implemented by subclasses ---

    @property
    @abstractmethod
    def source(self) -> ScraperSource:
        """
        Return the e-commerce platform identifier.
        
        Returns:
            ScraperSource enum value (AMAZON, NOON, etc)
        """
        ...

    @property
    @abstractmethod
    def base_url(self) -> str:
        """
        Return the root URL of the e-commerce platform.
        Used for validation and logging.
        
        Returns:
            Base URL as string (e.g., "https://www.amazon.com")
        """
        ...

    # --- Abstract methods - must be implemented by subclasses ---

    @abstractmethod
    def search_products(
        self,
        query:      str,
        max_pages:  Optional[int] = None,
        category:   Optional[str] = None,
    ) -> ScrapeResult:
        """
        Search for products matching query and gather data.
        Main entry point for scraping.
        
        Args:
            query: Search keyword/phrase
            max_pages: Override default max_pages from config
            category: Optional category filter
        
        Returns:
            ScrapeResult with products, errors, and metadata
        """
        ...

    @abstractmethod
    def get_product(self, url: str) -> Optional[Product]:
        """
        Fetch and parse a single product by URL.
        
        Args:
            url: Direct URL to product page
        
        Returns:
            Product object if successful, None on failure
        """
        ...

    @abstractmethod
    def _parse_product(self, raw: dict) -> Optional[Product]:
        """
        Parse raw product data into Product object.
        Site-specific extraction logic.
        
        Args:
            raw: Raw product data (dict, HTML object, etc)
        
        Returns:
            Product object if parsing successful, None if invalid
        """
        ...

    # --- Timing methods ---

    def _start(self) -> None:
        """Start timing for the current operation."""
        self._t0 = time.time()

    def _elapsed(self) -> float:
        """
        Get elapsed time since _start() was called.
        
        Returns:
            Elapsed seconds rounded to 2 decimal places
        """
        return round(time.time() - self._t0, 2)

    # --- Result building ---

    def _build_result(
        self,
        products: list[Product],
        errors:   list[str],
        pages:    int,
    ) -> ScrapeResult:
        """
        Construct a ScrapeResult from operation outcomes.
        Called at the end of a scrape operation.
        
        Args:
            products: List of successfully scraped products
            errors: List of error messages encountered
            pages: Number of pages processed
        
        Returns:
            Complete ScrapeResult object with metadata
        """
        return ScrapeResult(
            success          = len(products) > 0,
            products         = products,
            errors           = errors,
            pages_scraped    = pages,
            duration_seconds = self._elapsed(),
            source           = self.source,
        )
