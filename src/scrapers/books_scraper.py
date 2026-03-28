"""
src/scrapers/books_scraper.py

Live scraper for books.toscrape.com.
Legal, stable, and designed for scraping practice.

Author : M-D (Mohamed Darwish)
"""

import re
from decimal import Decimal
from typing import Optional

from bs4 import BeautifulSoup

from src.models.product import (
    Availability, Product, ProductPrice,
    ProductRating, ScraperSource, ScrapeResult,
)
from src.scrapers.base import BaseScraper, ScraperConfig
from src.utils.helpers import clean_text, normalise_url
from src.utils.http_client import HttpClient
from src.utils.logger import get_logger


logger = get_logger(__name__)

STAR_MAP = {"one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0, "five": 5.0}

CATEGORIES = [
    "mystery", "historical-fiction", "thriller", "romance", "fantasy",
    "science-fiction", "biography", "self-help", "business", "travel",
    "cookbooks", "poetry", "horror", "graphic-novels", "childrens",
    "young-adult", "classics", "crime", "sports", "music", "art",
    "philosophy", "psychology", "health", "parenting", "nonfiction",
    "fiction", "science", "technology", "history",
]


class BooksScraper(BaseScraper):

    @property
    def source(self) -> ScraperSource:
        return ScraperSource.BOOKS

    @property
    def base_url(self) -> str:
        return "https://books.toscrape.com"

    def search_products(
        self,
        query:     str            = "",
        max_pages: Optional[int]  = None,
        category:  Optional[str]  = None,
    ) -> ScrapeResult:
        self._start()
        limit     = max_pages or self.config.max_pages
        products: list[Product] = []
        errors:   list[str]     = []
        page      = 1

        if category:
            start = self._find_category_url(category)
            if not start:
                start = f"{self.base_url}/catalogue/page-1.html"
        else:
            start = f"{self.base_url}/catalogue/page-1.html"

        current = start

        while current and page <= limit:
            self.logger.info(f"Page {page}: {current}")
            resp = self.http.get(current)
            if resp is None:
                errors.append(f"Failed: page {page}")
                break

            soup = BeautifulSoup(resp.text, "lxml")
            pp, pe = self._parse_listing(soup)
            products.extend(pp)
            errors.extend(pe)
            self.logger.info(f"Page {page}: +{len(pp)} products ({len(products)} total)")
            current = self._next_url(soup, current)
            page += 1

        return self._build_result(products, errors, page - 1)

    def get_product(self, url: str) -> Optional[Product]:
        resp = self.http.get(url)
        if resp is None:
            return None
        soup = BeautifulSoup(resp.text, "lxml")
        raw  = self._extract_detail(soup, url)
        return self._parse_product(raw) if raw else None

    def get_categories(self) -> dict[str, str]:
        resp = self.http.get(self.base_url)
        if resp is None:
            return {}
        soup   = BeautifulSoup(resp.text, "lxml")
        result = {}
        for link in soup.select("ul.nav-stacked a"):
            name = clean_text(link.get_text())
            href = link.get("href", "")
            if name and href and name.lower() != "books":
                result[name] = normalise_url(href, self.base_url + "/")
        return result

    def _find_category_url(self, category: str) -> Optional[str]:
        cats = self.get_categories()
        for name, url in cats.items():
            if category.lower() in name.lower():
                return url
        return None

    def _parse_listing(self, soup: BeautifulSoup) -> tuple[list[Product], list[str]]:
        products, errors = [], []
        for article in soup.select("article.product_pod"):
            try:
                raw = self._extract_listing_raw(article)
                p   = self._parse_product(raw)
                if p:
                    products.append(p)
            except Exception as e:
                errors.append(str(e))
        return products, errors

    def _extract_listing_raw(self, article) -> dict:
        title_tag  = article.select_one("h3 > a")
        price_tag  = article.select_one("p.price_color")
        avail_tag  = article.select_one("p.availability")
        img_tag    = article.select_one("img")
        rating_tag = article.select_one("p.star-rating")

        rating_str = None
        if rating_tag:
            classes    = rating_tag.get("class", [])
            rating_str = next((c for c in classes if c.lower() in STAR_MAP), None)

        rel_url  = title_tag["href"] if title_tag else ""
        full_url = normalise_url(rel_url, f"{self.base_url}/catalogue/")

        return {
            "title":        title_tag.get("title", "") if title_tag else "",
            "price_str":    price_tag.get_text(strip=True) if price_tag else "",
            "availability": avail_tag.get_text(strip=True) if avail_tag else "",
            "rating_str":   rating_str,
            "url":          full_url,
            "image_url":    normalise_url(img_tag["src"] if img_tag else "", self.base_url),
            "source":       "listing",
        }

    def _extract_detail(self, soup: BeautifulSoup, url: str) -> Optional[dict]:
        try:
            title_tag  = soup.select_one("div.product_main h1")
            price_tag  = soup.select_one("p.price_color")
            avail_tag  = soup.select_one("p.availability")
            rating_tag = soup.select_one("p.star-rating")
            desc_tag   = soup.select_one("#product_description ~ p")
            img_tag    = soup.select_one("div.carousel-inner img")
            breadcrumbs = soup.select("ul.breadcrumb li")

            rating_str = None
            if rating_tag:
                classes    = rating_tag.get("class", [])
                rating_str = next((c for c in classes if c.lower() in STAR_MAP), None)

            info_table: dict[str, str] = {}
            for row in soup.select("table.table tr"):
                h = row.select_one("th")
                v = row.select_one("td")
                if h and v:
                    info_table[h.get_text(strip=True)] = v.get_text(strip=True)

            category = None
            if len(breadcrumbs) >= 3:
                category = breadcrumbs[-2].get_text(strip=True)

            avail_text = avail_tag.get_text(strip=True) if avail_tag else ""

            return {
                "title":        title_tag.get_text(strip=True) if title_tag else "",
                "price_str":    price_tag.get_text(strip=True) if price_tag else "",
                "availability": avail_text,
                "rating_str":   rating_str,
                "description":  desc_tag.get_text(strip=True) if desc_tag else None,
                "image_url":    normalise_url(img_tag["src"] if img_tag else "", self.base_url),
                "category":     category,
                "upc":          info_table.get("UPC"),
                "url":          url,
                "source":       "detail",
            }
        except Exception as e:
            logger.error(f"Detail extraction failed: {e}")
            return None

    def _parse_product(self, raw: dict) -> Optional[Product]:
        title = clean_text(raw.get("title"))
        url   = raw.get("url", "")
        if not title or not url:
            return None

        price_val = self._parse_gbp(raw.get("price_str", ""))
        if price_val is None:
            return None

        rating_str = raw.get("rating_str", "")
        score      = STAR_MAP.get(rating_str.lower()) if rating_str else None
        rating     = ProductRating(score=score) if score else None

        avail_text = raw.get("availability", "").lower()
        if "in stock" in avail_text:
            avail = Availability.IN_STOCK
        elif "out of stock" in avail_text:
            avail = Availability.OUT_OF_STOCK
        else:
            avail = Availability.UNKNOWN

        images = [raw["image_url"]] if raw.get("image_url") else []
        cat    = raw.get("category")
        tags   = [cat.lower()] if cat else []

        return Product(
            title        = title,
            url          = url,
            price        = ProductPrice(current=price_val, currency="GBP"),
            source       = ScraperSource.BOOKS,
            external_id  = raw.get("upc"),
            category     = cat,
            description  = clean_text(raw.get("description")),
            images       = images,
            rating       = rating,
            availability = avail,
            tags         = tags,
        )

    @staticmethod
    def _parse_gbp(price_str: str) -> Optional[Decimal]:
        match = re.search(r"[\d]+\.[\d]+", price_str)
        if match:
            try:
                return Decimal(match.group())
            except Exception:
                pass
        return None

    def _next_url(self, soup: BeautifulSoup, current: str) -> Optional[str]:
        btn = soup.select_one("li.next > a")
        if not btn:
            return None
        base = current.rsplit("/", 1)[0] + "/"
        return normalise_url(btn["href"], base)
