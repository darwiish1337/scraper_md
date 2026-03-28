"""
src/scrapers/simulated.py

Simulated scrapers for Amazon, Noon, AliExpress, Jumia, and eBay.

These generate realistic product data that mirrors what a real scraper
would collect. They exist because:
    1. These sites require authentication or JS rendering in production.
    2. The schema, distributions, and field names are identical to real output.
    3. Users can replace the _fetch_* methods with real implementations.

Each site has its own price range, currency, category set, and rating
distribution to reflect real-world differences.

Author : M-D (Mohamed Darwish)
"""

import random
import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from src.models.product import (
    Availability, Product, ProductPrice,
    ProductRating, ScraperSource, ScrapeResult,
)
from src.scrapers.base import BaseScraper, ScraperConfig
from src.utils.http_client import HttpClient
from src.utils.logger import get_logger


logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Shared data pools
# ---------------------------------------------------------------------------

BRANDS = {
    "Electronics": ["Samsung", "Apple", "Sony", "LG", "Xiaomi", "Huawei", "OnePlus", "Lenovo", "Dell", "HP", "Asus", "Acer"],
    "Fashion":     ["Nike", "Adidas", "Zara", "H&M", "Gucci", "Prada", "Calvin Klein", "Ralph Lauren", "Tommy Hilfiger"],
    "Home":        ["IKEA", "Philips", "Bosch", "Dyson", "Tefal", "Braun", "Black+Decker", "Electrolux"],
    "Books":       ["Penguin", "HarperCollins", "Random House", "Oxford", "McGraw-Hill", "Wiley"],
    "Sports":      ["Nike", "Adidas", "Puma", "Under Armour", "Reebok", "New Balance", "Decathlon"],
    "Beauty":      ["L'Oreal", "Maybelline", "MAC", "NYX", "Fenty Beauty", "Charlotte Tilbury", "Dior"],
    "Toys":        ["LEGO", "Mattel", "Hasbro", "Fisher-Price", "Hot Wheels", "Barbie"],
    "Automotive":  ["Bosch", "Michelin", "3M", "Castrol", "Shell", "Mobil", "NGK"],
    "Garden":      ["Husqvarna", "Bosch", "Gardena", "Black+Decker", "Flymo"],
    "Food":        ["Nestle", "Unilever", "Kraft", "Kellogg's", "Cadbury", "Lay's"],
}

ADJECTIVES = [
    "Premium", "Professional", "Advanced", "Ultra", "Pro", "Elite",
    "Classic", "Deluxe", "Essential", "Smart", "Portable", "Wireless",
    "Compact", "Heavy Duty", "Lightweight", "High Performance",
]

NOUNS = {
    "Electronics": ["Laptop", "Smartphone", "Tablet", "Headphones", "Speaker", "Monitor", "Keyboard", "Mouse", "Webcam", "Smartwatch", "Earbuds", "Router", "SSD", "Power Bank", "Projector"],
    "Fashion":     ["T-Shirt", "Jeans", "Sneakers", "Jacket", "Dress", "Hoodie", "Shorts", "Shirt", "Trousers", "Shoes", "Bag", "Wallet", "Watch", "Sunglasses"],
    "Home":        ["Blender", "Coffee Maker", "Air Fryer", "Vacuum Cleaner", "Iron", "Toaster", "Kettle", "Lamp", "Fan", "Heater", "Pillow", "Curtains", "Rug", "Frame"],
    "Books":       ["Complete Guide", "Handbook", "Masterclass", "Fundamentals", "Advanced Course", "Workbook", "Reference Manual"],
    "Sports":      ["Running Shoes", "Yoga Mat", "Dumbbell Set", "Resistance Bands", "Jump Rope", "Water Bottle", "Gym Gloves", "Backpack", "Cycling Helmet", "Tennis Racket"],
    "Beauty":      ["Face Cream", "Foundation", "Mascara", "Lipstick", "Serum", "Moisturiser", "Perfume", "Shampoo", "Conditioner", "Nail Polish"],
    "Toys":        ["Building Set", "Action Figure", "Board Game", "Remote Control Car", "Puzzle", "Doll", "Science Kit", "Art Set"],
    "Automotive":  ["Car Mat", "Dash Camera", "Car Charger", "Air Freshener", "Tool Kit", "Jump Starter", "Tyre Inflator"],
    "Garden":      ["Plant Pot", "Garden Hose", "Pruning Shears", "Watering Can", "Soil Mix", "Fertiliser", "Seed Pack"],
    "Food":        ["Protein Bar", "Multivitamin", "Green Tea", "Olive Oil", "Honey", "Nuts Mix", "Granola", "Dried Fruits"],
}

DESCRIPTIONS = [
    "Built for everyday use with durable materials and ergonomic design.",
    "Engineered for performance with precision components and reliable construction.",
    "A trusted choice for professionals and enthusiasts alike.",
    "Designed to simplify your daily routine without compromising on quality.",
    "Compact form, powerful results — an ideal solution for modern lifestyles.",
    "Crafted with attention to detail and backed by comprehensive warranty coverage.",
    "A versatile product suitable for a wide range of applications and users.",
    "High-quality construction ensures long-term reliability and consistent performance.",
    "Thoughtfully designed to deliver value without cutting corners on key features.",
    "Combining modern aesthetics with functional engineering for discerning users.",
]


def _random_title(category: str) -> str:
    brand = random.choice(BRANDS.get(category, ["Generic"]))
    adj   = random.choice(ADJECTIVES) if random.random() < 0.6 else ""
    noun  = random.choice(NOUNS.get(category, ["Product"]))
    parts = [p for p in [brand, adj, noun] if p]
    extra = random.choice(["", "2024", "v2", "Plus", "Max", "Lite", "Pro"])
    if extra:
        parts.append(extra)
    return " ".join(parts)


def _random_product(
    source:    ScraperSource,
    category:  str,
    price_min: float,
    price_max: float,
    currency:  str,
    base_url:  str,
    idx:       int,
) -> Product:
    title     = _random_title(category)
    brand     = title.split()[0]
    raw_price = round(random.uniform(price_min, price_max), 2)
    price_val = Decimal(str(raw_price))

    original = None
    if random.random() < 0.30:
        markup   = Decimal(str(round(random.uniform(1.05, 1.45), 2)))
        original = (price_val * markup).quantize(Decimal("0.01"))

    score    = None
    reviews  = 0
    if random.random() < 0.80:
        score   = round(random.uniform(2.5, 5.0), 1)
        reviews = max(1, int(random.expovariate(0.003)))
        reviews = min(reviews, 200_000)

    avail_roll = random.random()
    if avail_roll < 0.83:
        avail = Availability.IN_STOCK
    elif avail_roll < 0.92:
        avail = Availability.LIMITED
    else:
        avail = Availability.OUT_OF_STOCK

    slug      = re.sub(r"[^a-z0-9]+", "-", title.lower())[:60].strip("-")
    url       = f"{base_url}/product/{slug}-{idx}"
    upc       = "".join(random.choices("0123456789", k=13))
    days_ago  = random.uniform(0, 14)
    scraped   = datetime.utcnow() - timedelta(days=days_ago)
    tags      = [category.lower(), source.value]

    return Product(
        title        = title,
        url          = url,
        price        = ProductPrice(current=price_val, original=original, currency=currency),
        source       = source,
        external_id  = upc,
        brand        = brand,
        category     = category,
        description  = random.choice(DESCRIPTIONS),
        images       = [f"https://cdn.{source.value}.example/img/{upc}.jpg"],
        rating       = ProductRating(score=score, reviews_count=reviews) if score else None,
        availability = avail,
        scraped_at   = scraped,
        tags         = tags,
    )


# ---------------------------------------------------------------------------
# Site configurations
# ---------------------------------------------------------------------------

_SITE_CONFIG = {
    ScraperSource.AMAZON: {
        "base_url":   "https://www.amazon.com",
        "currency":   "USD",
        "price_min":  5.0,
        "price_max":  2500.0,
        "categories": list(NOUNS.keys()),
    },
    ScraperSource.NOON: {
        "base_url":   "https://www.noon.com",
        "currency":   "AED",
        "price_min":  20.0,
        "price_max":  8000.0,
        "categories": ["Electronics", "Fashion", "Home", "Beauty", "Sports", "Toys", "Food"],
    },
    ScraperSource.ALIEXPRESS: {
        "base_url":   "https://www.aliexpress.com",
        "currency":   "USD",
        "price_min":  0.5,
        "price_max":  500.0,
        "categories": list(NOUNS.keys()),
    },
    ScraperSource.JUMIA: {
        "base_url":   "https://www.jumia.com.eg",
        "currency":   "EGP",
        "price_min":  50.0,
        "price_max":  50000.0,
        "categories": ["Electronics", "Fashion", "Home", "Beauty", "Sports", "Food", "Automotive"],
    },
    ScraperSource.EBAY: {
        "base_url":   "https://www.ebay.com",
        "currency":   "USD",
        "price_min":  1.0,
        "price_max":  3000.0,
        "categories": list(NOUNS.keys()),
    },
}


# ---------------------------------------------------------------------------
# Base for all simulated scrapers
# ---------------------------------------------------------------------------

class SimulatedScraper(BaseScraper):
    """
    Base for all simulated scrapers.
    Subclasses only declare source and optionally override config.
    """

    def __init__(self, config: ScraperConfig, http_client: HttpClient):
        super().__init__(config, http_client)
        self._cfg = _SITE_CONFIG[self.source]

    @property
    def base_url(self) -> str:
        return self._cfg["base_url"]

    def search_products(
        self,
        query:     str           = "",
        max_pages: Optional[int] = None,
        category:  Optional[str] = None,
    ) -> ScrapeResult:
        self._start()
        random.seed()

        limit = max_pages or self.config.max_pages
        per_page = 20

        # Determine which categories to generate from
        all_cats = self._cfg["categories"]
        if category:
            cats = [c for c in all_cats if category.lower() in c.lower()]
            if not cats:
                cats = all_cats
        elif query:
            # Bias toward categories that match the query keyword
            cats = [c for c in all_cats if query.lower() in c.lower()] or all_cats
        else:
            cats = all_cats

        products: list[Product] = []
        total    = limit * per_page

        for i in range(total):
            cat = random.choice(cats)
            p   = _random_product(
                source    = self.source,
                category  = cat,
                price_min = self._cfg["price_min"],
                price_max = self._cfg["price_max"],
                currency  = self._cfg["currency"],
                base_url  = self.base_url,
                idx       = i + 1,
            )
            products.append(p)

        self.logger.info(
            f"Generated {len(products)} products for {self.source.value}"
        )
        return self._build_result(products, [], limit)

    def get_product(self, url: str) -> Optional[Product]:
        # Single product — generate one realistic item
        cat = random.choice(self._cfg["categories"])
        return _random_product(
            source    = self.source,
            category  = cat,
            price_min = self._cfg["price_min"],
            price_max = self._cfg["price_max"],
            currency  = self._cfg["currency"],
            base_url  = self.base_url,
            idx       = 1,
        )

    def _parse_product(self, raw: dict) -> Optional[Product]:
        # Not used in simulated scrapers (no HTML to parse)
        return None

    def available_categories(self) -> list[str]:
        return self._cfg["categories"]


# ---------------------------------------------------------------------------
# Concrete simulated scrapers — one class per site
# ---------------------------------------------------------------------------

class AmazonScraper(SimulatedScraper):
    @property
    def source(self) -> ScraperSource:
        return ScraperSource.AMAZON


class NoonScraper(SimulatedScraper):
    @property
    def source(self) -> ScraperSource:
        return ScraperSource.NOON


class AliExpressScraper(SimulatedScraper):
    @property
    def source(self) -> ScraperSource:
        return ScraperSource.ALIEXPRESS


class JumiaScraper(SimulatedScraper):
    @property
    def source(self) -> ScraperSource:
        return ScraperSource.JUMIA


class EbayScraper(SimulatedScraper):
    @property
    def source(self) -> ScraperSource:
        return ScraperSource.EBAY
