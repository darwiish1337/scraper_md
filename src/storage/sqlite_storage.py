"""
src/storage/sqlite_storage.py

SQLite repository for products and scrape run history.

Author : M-D (Mohamed Darwish)
"""

import json
import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

from src.models.product import (
    Availability, Product, ProductPrice,
    ProductRating, ScraperSource, ScrapeResult,
)
from src.utils.logger import get_logger


logger = get_logger(__name__)


class SQLiteStorage:

    def __init__(self, db_path: str = "data/scraper.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_schema(self) -> None:
        conn = self._connect()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id      TEXT PRIMARY KEY,
                    external_id     TEXT,
                    title           TEXT NOT NULL,
                    brand           TEXT,
                    category        TEXT,
                    subcategory     TEXT,
                    url             TEXT NOT NULL UNIQUE,
                    source          TEXT NOT NULL,
                    price_current   REAL NOT NULL,
                    price_original  REAL,
                    currency        TEXT DEFAULT 'USD',
                    discount_pct    REAL,
                    has_discount    INTEGER DEFAULT 0,
                    rating_score    REAL,
                    reviews_count   INTEGER DEFAULT 0,
                    availability    TEXT DEFAULT 'unknown',
                    description     TEXT,
                    images_json     TEXT,
                    tags_json       TEXT,
                    scraped_at      TEXT NOT NULL,
                    created_at      TEXT DEFAULT (datetime('now'))
                );
                CREATE INDEX IF NOT EXISTS idx_source    ON products (source);
                CREATE INDEX IF NOT EXISTS idx_category  ON products (category);
                CREATE INDEX IF NOT EXISTS idx_scraped   ON products (scraped_at);

                CREATE TABLE IF NOT EXISTS scrape_runs (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    source           TEXT NOT NULL,
                    total_products   INTEGER DEFAULT 0,
                    pages_scraped    INTEGER DEFAULT 0,
                    duration_seconds REAL    DEFAULT 0,
                    errors_count     INTEGER DEFAULT 0,
                    success          INTEGER DEFAULT 0,
                    started_at       TEXT NOT NULL
                );
            """)
            conn.commit()
        finally:
            conn.close()

    def save_products(self, products: list[Product]) -> int:
        if not products:
            return 0
        rows = [self._to_row(p) for p in products]
        conn = self._connect()
        try:
            conn.executemany("""
                INSERT OR REPLACE INTO products (
                    product_id, external_id, title, brand, category, subcategory,
                    url, source, price_current, price_original, currency,
                    discount_pct, has_discount, rating_score, reviews_count,
                    availability, description, images_json, tags_json, scraped_at
                ) VALUES (
                    :product_id,:external_id,:title,:brand,:category,:subcategory,
                    :url,:source,:price_current,:price_original,:currency,
                    :discount_pct,:has_discount,:rating_score,:reviews_count,
                    :availability,:description,:images_json,:tags_json,:scraped_at
                )
            """, rows)
            conn.commit()
            logger.info(f"Saved {len(rows)} products to database")
            return len(rows)
        finally:
            conn.close()

    def log_run(self, result: ScrapeResult) -> None:
        conn = self._connect()
        try:
            conn.execute("""
                INSERT INTO scrape_runs
                    (source, total_products, pages_scraped, duration_seconds,
                     errors_count, success, started_at)
                VALUES (?,?,?,?,?,?,?)
            """, (
                result.source.value if result.source else "unknown",
                result.total_products, result.pages_scraped,
                result.duration_seconds, len(result.errors),
                int(result.success), datetime.utcnow().isoformat(),
            ))
            conn.commit()
        finally:
            conn.close()

    def get_all_dicts(self) -> list[dict]:
        conn = self._connect()
        try:
            return [dict(r) for r in conn.execute("SELECT * FROM products ORDER BY scraped_at DESC").fetchall()]
        finally:
            conn.close()

    def get_by_source(self, source: str) -> list[dict]:
        conn = self._connect()
        try:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM products WHERE source=? ORDER BY price_current", (source,)
            ).fetchall()]
        finally:
            conn.close()

    def get_stats(self) -> dict:
        conn = self._connect()
        try:
            row = conn.execute("""
                SELECT
                    COUNT(*)                  AS total_products,
                    COUNT(DISTINCT source)    AS sources,
                    COUNT(DISTINCT category)  AS categories,
                    ROUND(AVG(price_current),2) AS avg_price,
                    ROUND(MIN(price_current),2) AS min_price,
                    ROUND(MAX(price_current),2) AS max_price,
                    SUM(has_discount)         AS discounted,
                    ROUND(AVG(rating_score),2) AS avg_rating,
                    MAX(scraped_at)           AS last_scraped
                FROM products
            """).fetchone()
            return dict(row) if row else {}
        finally:
            conn.close()

    def total_count(self) -> int:
        conn = self._connect()
        try:
            return conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        finally:
            conn.close()

    def clear_source(self, source: str) -> int:
        conn = self._connect()
        try:
            cur = conn.execute("DELETE FROM products WHERE source=?", (source,))
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()

    def clear_all(self) -> int:
        conn = self._connect()
        try:
            cur1 = conn.execute("DELETE FROM products")
            cur2 = conn.execute("DELETE FROM scrape_runs")
            conn.commit()
            return cur1.rowcount
        finally:
            conn.close()

    @staticmethod
    def _to_row(p: Product) -> dict:
        return {
            "product_id":    str(p.product_id),
            "external_id":   p.external_id,
            "title":         p.title,
            "brand":         p.brand,
            "category":      p.category,
            "subcategory":   p.subcategory,
            "url":           p.url,
            "source":        p.source.value,
            "price_current": float(p.price.current),
            "price_original": float(p.price.original) if p.price.original else None,
            "currency":      p.price.currency,
            "discount_pct":  p.price.discount_percentage,
            "has_discount":  int(p.price.has_discount),
            "rating_score":  p.rating.score if p.rating else None,
            "reviews_count": p.rating.reviews_count if p.rating else 0,
            "availability":  p.availability.value,
            "description":   p.description,
            "images_json":   json.dumps(p.images),
            "tags_json":     json.dumps(p.tags),
            "scraped_at":    p.scraped_at.isoformat(),
        }

    def __enter__(self) -> "SQLiteStorage":
        return self

    def __exit__(self, *_) -> None:
        pass
