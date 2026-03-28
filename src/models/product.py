"""
src/models/product.py

Core domain models. No I/O, no side effects.

Author : M-D (Mohamed Darwish)
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class Availability(str, Enum):
    IN_STOCK     = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    LIMITED      = "limited"
    UNKNOWN      = "unknown"


class ScraperSource(str, Enum):
    AMAZON   = "amazon"
    NOON     = "noon"
    ALIEXPRESS = "aliexpress"
    JUMIA    = "jumia"
    EBAY     = "ebay"
    BOOKS    = "books_toscrape"
    CUSTOM   = "custom"


@dataclass
class ProductPrice:
    current:  Decimal
    original: Optional[Decimal] = None
    currency: str               = "USD"

    @property
    def discount_amount(self) -> Optional[Decimal]:
        if self.original and self.original > self.current:
            return (self.original - self.current).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        return None

    @property
    def discount_percentage(self) -> Optional[float]:
        if self.original and self.original > 0 and self.discount_amount:
            return float(
                (self.discount_amount / self.original * 100)
                .quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            )
        return None

    @property
    def has_discount(self) -> bool:
        return self.discount_percentage is not None

    def __str__(self) -> str:
        return f"{self.currency} {self.current:.2f}"


@dataclass
class ProductRating:
    score:         Optional[float] = None
    reviews_count: int             = 0

    def is_reliable(self, min_reviews: int = 10) -> bool:
        return self.reviews_count >= min_reviews


@dataclass
class Product:
    title:        str
    url:          str
    price:        ProductPrice
    source:       ScraperSource
    product_id:   UUID                    = field(default_factory=uuid4)
    external_id:  Optional[str]           = None
    brand:        Optional[str]           = None
    category:     Optional[str]           = None
    subcategory:  Optional[str]           = None
    description:  Optional[str]           = None
    images:       list[str]               = field(default_factory=list)
    rating:       Optional[ProductRating] = None
    availability: Availability            = Availability.UNKNOWN
    scraped_at:   datetime                = field(default_factory=datetime.utcnow)
    tags:         list[str]               = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "product_id":     str(self.product_id),
            "external_id":    self.external_id,
            "title":          self.title,
            "brand":          self.brand,
            "category":       self.category,
            "subcategory":    self.subcategory,
            "url":            self.url,
            "source":         self.source.value,
            "price_current":  float(self.price.current),
            "price_original": float(self.price.original) if self.price.original else None,
            "currency":       self.price.currency,
            "discount_pct":   self.price.discount_percentage,
            "has_discount":   self.price.has_discount,
            "rating_score":   self.rating.score if self.rating else None,
            "reviews_count":  self.rating.reviews_count if self.rating else 0,
            "availability":   self.availability.value,
            "description":    self.description,
            "images_count":   len(self.images),
            "first_image":    self.images[0] if self.images else None,
            "tags":           "|".join(self.tags),
            "scraped_at":     self.scraped_at.isoformat(),
        }

    def __repr__(self) -> str:
        return (
            f"Product(source={self.source.value!r}, "
            f"title={self.title[:45]!r}, "
            f"price={self.price})"
        )


@dataclass
class ScrapeResult:
    success:          bool
    products:         list[Product]       = field(default_factory=list)
    errors:           list[str]           = field(default_factory=list)
    pages_scraped:    int                 = 0
    duration_seconds: float              = 0.0
    source:           Optional[ScraperSource] = None

    @property
    def total_products(self) -> int:
        return len(self.products)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
