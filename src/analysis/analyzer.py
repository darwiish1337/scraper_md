"""
src/analysis/analyzer.py

Statistical analysis on scraped product data.

Author : M-D (Mohamed Darwish)
"""

import statistics
from collections import Counter, defaultdict

from src.models.product import Product
from src.utils.logger import get_logger


logger = get_logger(__name__)


class ProductAnalyzer:

    def __init__(self, products: list[Product]):
        if not products:
            raise ValueError("Cannot analyse an empty list.")
        self.products = products

    def price_statistics(self) -> dict:
        prices = [float(p.price.current) for p in self.products if p.price.current > 0]
        if not prices:
            return {}
        prices.sort()
        n = len(prices)

        def pct(p: float) -> float:
            return round(prices[int(p / 100 * (n - 1))], 2)

        return {
            "count":   n,
            "mean":    round(statistics.mean(prices), 2),
            "median":  round(statistics.median(prices), 2),
            "std_dev": round(statistics.stdev(prices), 2) if n > 1 else 0,
            "min":     round(min(prices), 2),
            "max":     round(max(prices), 2),
            "p25":     pct(25),
            "p75":     pct(75),
            "p90":     pct(90),
        }

    def by_category(self) -> list[dict]:
        grouped: dict[str, list[Product]] = defaultdict(list)
        for p in self.products:
            grouped[p.category or "Unknown"].append(p)

        result = []
        for cat, items in grouped.items():
            prices     = [float(p.price.current) for p in items if p.price.current > 0]
            rated      = [p.rating.score for p in items if p.rating and p.rating.score]
            discounted = sum(1 for p in items if p.price.has_discount)
            result.append({
                "category":     cat,
                "count":        len(items),
                "avg_price":    round(statistics.mean(prices), 2) if prices else None,
                "avg_rating":   round(statistics.mean(rated), 2) if rated else None,
                "discount_pct": round(discounted / len(items) * 100, 1),
            })

        return sorted(result, key=lambda x: x["count"], reverse=True)

    def by_source(self) -> list[dict]:
        grouped: dict[str, list[Product]] = defaultdict(list)
        for p in self.products:
            grouped[p.source.value].append(p)
        result = []
        for source, items in grouped.items():
            prices = [float(p.price.current) for p in items if p.price.current > 0]
            rated  = [p.rating.score for p in items if p.rating and p.rating.score]
            result.append({
                "source":     source,
                "count":      len(items),
                "avg_price":  round(statistics.mean(prices), 2) if prices else None,
                "avg_rating": round(statistics.mean(rated), 2) if rated else None,
                "currency":   items[0].price.currency if items else "?",
            })
        return sorted(result, key=lambda x: x["count"], reverse=True)

    def top_rated(self, n: int = 10) -> list[Product]:
        rated = [p for p in self.products if p.rating and p.rating.score and p.rating.reviews_count >= 5]
        return sorted(rated, key=lambda p: p.rating.score, reverse=True)[:n]

    def best_discounts(self, n: int = 10) -> list[Product]:
        disc = [p for p in self.products if p.price.has_discount]
        return sorted(disc, key=lambda p: p.price.discount_percentage or 0, reverse=True)[:n]

    def cheapest(self, n: int = 10) -> list[Product]:
        return sorted(self.products, key=lambda p: p.price.current)[:n]

    def most_expensive(self, n: int = 10) -> list[Product]:
        return sorted(self.products, key=lambda p: p.price.current, reverse=True)[:n]

    def availability_summary(self) -> dict:
        counts = Counter(p.availability.value for p in self.products)
        total  = len(self.products)
        return {k: {"count": v, "pct": round(v / total * 100, 1)} for k, v in counts.items()}

    def full_report(self) -> dict:
        return {
            "total":               len(self.products),
            "price_statistics":    self.price_statistics(),
            "by_category":         self.by_category()[:20],
            "by_source":           self.by_source(),
            "availability":        self.availability_summary(),
            "top_rated":           [p.to_dict() for p in self.top_rated(10)],
            "best_discounts":      [p.to_dict() for p in self.best_discounts(10)],
        }
