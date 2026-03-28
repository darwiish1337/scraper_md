"""
src/pipeline/cleaner.py

Data cleaning — runs after every scrape before storage.

Author : M-D (Mohamed Darwish)
"""

import re
from decimal import Decimal
from typing import Optional

from src.models.product import Product
from src.utils.logger import get_logger


logger = get_logger(__name__)

MAX_PRICE = Decimal("1_000_000")


def clean_products(products: list[Product]) -> list[Product]:
    """
    Validate, normalise, and deduplicate a list of raw products.
    Returns a new list — originals are not mutated.
    """
    if not products:
        return []

    before  = len(products)
    cleaned = [_clean_one(p) for p in products]
    cleaned = [p for p in cleaned if p is not None]
    cleaned = _dedup(cleaned)
    after   = len(cleaned)

    if before != after:
        logger.info(f"Cleaning: {before} → {after} products ({before - after} removed)")
    return cleaned


def _clean_one(product: Product) -> Optional[Product]:
    if not product.title or not product.title.strip():
        return None
    if not product.url or not product.url.startswith("http"):
        return None
    if product.price.current < Decimal("0"):
        return None
    if product.price.current > MAX_PRICE:
        return None

    product.title       = re.sub(r"\s+", " ", product.title.strip())
    product.tags        = sorted(set(t.lower().strip() for t in product.tags if t.strip()))
    if product.description and len(product.description) > 1000:
        product.description = product.description[:997] + "..."
    if product.brand:
        product.brand = product.brand.strip()
    if product.category:
        product.category = product.category.strip()
    return product


def _dedup(products: list[Product]) -> list[Product]:
    seen:   set[str]     = set()
    unique: list[Product] = []
    for p in products:
        key = p.url.rstrip("/").lower()
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique
