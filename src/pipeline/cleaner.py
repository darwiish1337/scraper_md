"""
src/pipeline/cleaner.py

Data cleaning and validation pipeline.
Runs after every scrape before storage to ensure data quality.

Key Operations:
    1. Validation: Remove invalid/incomplete products
    2. Normalization: Fix formatting and whitespace
    3. Deduplication: Remove exact URL duplicates
    4. Range checks: Ensure prices are reasonable

All operations are documented so data loss can be tracked.

Author : M-D (Mohamed Darwish)
"""

import re
from decimal import Decimal
from typing import Optional

from src.models.product import Product
from src.utils.logger import get_logger


logger = get_logger(__name__)

# Maximum reasonable price (prevents data entry errors)
MAX_PRICE = Decimal("1_000_000")


def clean_products(products: list[Product]) -> list[Product]:
    """
    Validate, normalize, and deduplicate a list of raw products.
    
    This is the main entry point for data cleaning. It applies all
    cleaning operations in sequence and logs the overall impact.
    
    Args:
        products: Raw products from scraper
    
    Returns:
        Cleaned list of products (originals are not modified)
    
    Example:
        raw_products = scraper.search_products("laptop", max_pages=3)
        cleaned = clean_products(raw_products.products)
        print(f"Removed {len(raw_products) - len(cleaned)} invalid items")
    """
    if not products:
        return []

    before  = len(products)
    
    # Step 1: Clean individual products
    cleaned = [_clean_one(p) for p in products]
    cleaned = [p for p in cleaned if p is not None]
    
    # Step 2: Remove duplicates (by URL)
    cleaned = _dedup(cleaned)
    
    after   = len(cleaned)
    removed = before - after

    # Log cleaning statistics
    if removed > 0:
        logger.info(
            f"Data cleaning: {before} → {after} products "
            f"({removed} invalid items removed, "
            f"{(removed/before*100):.1f}%)"
        )
    return cleaned


def _clean_one(product: Product) -> Optional[Product]:
    """
    Validate and normalize a single product.
    
    Validation checks:
        - Title is not empty
        - URL is valid (starts with http)
        - Price is non-negative and reasonable
    
    Normalization:
        - Collapse multiple spaces to single space
        - Remove duplicate tags (case-insensitive)
        - Truncate long descriptions with ellipsis
        - Trim whitespace from text fields
    
    Args:
        product: Product to clean
    
    Returns:
        Cleaned product or None if validation failed
    """
    # --- Validation ---
    
    # Title is required and must not be empty
    if not product.title or not product.title.strip():
        return None
    
    # URL is required and must be absolute
    if not product.url or not product.url.startswith("http"):
        return None
    
    # Price cannot be negative
    if product.price.current < Decimal("0"):
        return None
    
    # Price must be reasonable (prevents data entry errors and outliers)
    if product.price.current > MAX_PRICE:
        return None

    # --- Normalization ---
    
    # Normalize whitespace in title (multiple spaces → single space)
    product.title = re.sub(r"\s+", " ", product.title.strip())
    
    # Deduplicate tags and convert to lowercase for consistency
    product.tags = sorted(set(
        t.lower().strip() 
        for t in product.tags 
        if t.strip()
    ))
    
    # Truncate excessively long descriptions
    if product.description and len(product.description) > 1000:
        product.description = product.description[:997] + "..."
    
    # Trim whitespace from optional text fields
    if product.brand:
        product.brand = product.brand.strip()
    
    if product.category:
        product.category = product.category.strip()
    
    return product


def _dedup(products: list[Product]) -> list[Product]:
    """
    Remove duplicate products based on URL.
    
    Deduplication strategy:
        - URLs are normalized (trailing slashes removed, lowercased)
        - First occurrence is kept, duplicates are discarded
        - Preserves original product object (including tags, etc)
    
    Args:
        products: Product list with potential duplicates
    
    Returns:
        List with duplicates removed, preserving order and first occurrence
    """
    seen:   set[str]     = set()
    unique: list[Product] = []
    
    for p in products:
        # Normalize URL for comparison
        key = p.url.rstrip("/").lower()
        
        # Keep only first occurrence
        if key not in seen:
            seen.add(key)
            unique.append(p)
    
    return unique
