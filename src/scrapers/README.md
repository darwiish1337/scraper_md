# 🕷️ Scrapers Module

This module handles all data collection logic across different e-commerce platforms.

---

## 📁 Structure

```
scrapers/
├── __init__.py              Module exports
├── base.py                  Abstract base class (contract)
├── simulated.py             Simulated scrapers (Amazon, Noon, AliExpress, Jumia, eBay)
├── books_scraper.py         Live scraper (Books to Scrape)
├── factory.py               Registry and scraper creation
└── custom_sites.py          User-added site persistence
```

---

## 🏗️ Architecture

### Base Contract: `BaseScraper`

All scrapers inherit from `BaseScraper` and implement:

```python
from src.scrapers.base import BaseScraper

class MyScraper(BaseScraper):
    
    @property
    def source(self) -> ScraperSource:
        """Return site identifier."""
        return ScraperSource.AMAZON
    
    def search_products(self, query: str, pages: int = 5) -> SearchResult:
        """
        Find products matching query keyword.
        
        Args:
            query: Search term (e.g., "laptop")
            pages: Number of pages to fetch
        
        Returns:
            SearchResult with products list and total count
        """
        # Your implementation here
        pass
    
    def get_product(self, product_id: str) -> Product | None:
        """Fetch single product details by ID."""
        pass
    
    def _parse_product(self, raw_data: dict) -> Product:
        """Convert raw response to Product model."""
        pass
```

### Available Implementations

| Scraper | File | Mode | Status |
|---------|------|------|--------|
| Amazon | simulated.py | Simulated | ✅ Working |
| Noon | simulated.py | Simulated | ✅ Working |
| AliExpress | simulated.py | Simulated | ✅ Working |
| Jumia | simulated.py | Simulated | ✅ Working |
| eBay | simulated.py | Simulated | ✅ Working |
| Books to Scrape | books_scraper.py | Live | ✅ Working |

---

## 🔧 How Scrapers Are Created

### Registry System (`factory.py`)

Scrapers are registered by name and accessed through a factory:

```python
from src.scrapers.factory import create_scraper, list_sites, REGISTRY

# List all available sites
print(list_sites())  # ['amazon', 'noon', 'aliexpress', 'jumia', 'ebay', 'bookscapes']

# Create a scraper for a site
scraper = create_scraper('amazon')
result = scraper.search_products('laptop', pages=5)
```

### Custom Sites System

User-added sites are stored in `data/custom_sites.json` and auto-loaded:

```python
from src.scrapers.factory import load_saved_custom_sites

# Call on app startup to fetch user's custom sites
load_saved_custom_sites()

# Now they're available to scrape
scraper = create_scraper('mystore')
```

---

## 🆕 Adding a New Platform

### Step 1: Create Scraper Class

**File:** `src/scrapers/mysite_scraper.py`

```python
from src.scrapers.base import BaseScraper
from src.models.product import Product, SearchResult
from src.utils.http_client import HttpClient

class MySiteScraper(BaseScraper):
    """Scraper for MyStore e-commerce platform."""
    
    def __init__(self, http_client: HttpClient):
        super().__init__(http_client)
        self.base_url = "https://mysite.example.com"
    
    @property
    def source(self) -> str:
        return "mysite"
    
    def search_products(self, query: str, pages: int = 5) -> SearchResult:
        """Search for products on MyStore."""
        products = []
        
        for page in range(1, pages + 1):
            url = f"{self.base_url}/search"
            params = {"q": query, "page": page}
            
            response = self._fetch(url, params=params)
            if not response:
                break
            
            page_items = self._parse_page(response)
            products.extend(page_items)
        
        return SearchResult(
            products=products,
            total_products=len(products)
        )
    
    def get_product(self, product_id: str) -> Product | None:
        """Fetch single product by ID."""
        url = f"{self.base_url}/products/{product_id}"
        response = self._fetch(url)
        
        if response:
            return self._parse_product(response)
        return None
    
    def _parse_product(self, raw_data: dict) -> Product:
        """Convert raw JSON to Product model."""
        return Product(
            product_id=raw_data.get('id'),
            title=raw_data.get('name'),
            brand=raw_data.get('brand'),
            price_current=float(raw_data.get('price', 0)),
            currency="USD",
            source=self.source,
            # ... map other fields
        )
    
    def _parse_page(self, html: str) -> list[Product]:
        """Parse HTML page for products."""
        # Use BeautifulSoup or regex
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        products = []
        for item in soup.select('.product-item'):
            product = self._parse_product({
                'id': item.get('data-id'),
                'name': item.select_one('.title')?.text,
                'brand': item.select_one('.brand')?.text,
                'price': float(item.select_one('.price')?.text.replace('$', '')),
            })
            products.append(product)
        
        return products
```

### Step 2: Register in Factory

**File:** `src/scrapers/factory.py`

```python
from src.scrapers.mysite_scraper import MySiteScraper

# Add to REGISTRY dict
REGISTRY["mysite"] = SiteInfo(
    name="MyStore",
    description="Premium e-commerce platform",
    currency="USD",
    mode="live",  # or "simulated"
    scraper_cls=MySiteScraper,
)
```

### Step 3: Done! Now you can use it:

```bash
python main.py scrape mysite 10
python main.py scrape mysite 5 -q "laptop"
python main.py scrape mysite 10 -c Electronics
```

---

## 📦 Import Utilities

### HttpClient

Handles requests with retries, delays, and user-agent rotation:

```python
from src.utils.http_client import HttpClient

http = HttpClient()

# GET request with auto-retry
response = http.get(
    url="https://example.com/products",
    params={"page": 1},
    timeout=30
)

# POST request
response = http.post(
    url="https://example.com/search",
    json={"query": "laptop"},
    timeout=30
)
```

### Models

Domain models for type safety:

```python
from src.models.product import Product, SearchResult

# Create product
product = Product(
    product_id="abc123",
    title="Laptop",
    price_current=999.99,
    currency="USD",
    source="amazon",
    # ... other fields
)

# Create search result
result = SearchResult(
    products=[product],
    total_products=1
)
```

### Data Pipeline

Clean and validate data:

```python
from src.pipeline.cleaner import DataCleaner

cleaner = DataCleaner()
cleaned_products = cleaner.clean(raw_products)
```

---

## 🧪 Testing Your Scraper

### Manual Test

```python
from src.utils.http_client import HttpClient
from src.scrapers.mysite_scraper import MySiteScraper

# Create scraper
http = HttpClient()
scraper = MySiteScraper(http)

# Test search
result = scraper.search_products("laptop", pages=1)
print(f"Found {result.total_products} products")

# Test single product
product = scraper.get_product("abc123")
print(f"Product: {product.title} - ${product.price_current}")
```

### With Pytest

```python
# tests/test_mysite_scraper.py

import pytest
from src.scrapers.mysite_scraper import MySiteScraper
from src.utils.http_client import HttpClient

def test_search_returns_products():
    scraper = MySiteScraper(HttpClient())
    result = scraper.search_products("test", pages=1)
    
    assert result.total_products > 0
    assert len(result.products) > 0

def test_product_has_required_fields():
    scraper = MySiteScraper(HttpClient())
    result = scraper.search_products("test", pages=1)
    product = result.products[0]
    
    assert product.product_id
    assert product.title
    assert product.price_current is not None
```

---

## 🎯 Simulated vs Live Scrapers

### Simulated Scraper

- Generates realistic, fake data
- No HTTP requests (super fast)
- Perfect for testing, demos, development
- Inherits from `SimulatedScraper`

```python
from src.scrapers.simulated import SimulatedScraper

class FakeShopScraper(SimulatedScraper):
    @property
    def source(self) -> str:
        return "fakeshop"
```

### Live Scraper

- Makes real HTTP requests
- Hit actual websites
- Must respect `robots.txt` and terms
- Implement `BaseScraper` directly

```python
from src.scrapers.base import BaseScraper

class RealShopScraper(BaseScraper):
    # make real HTTP calls
    pass
```

---

## ⚙️ Using Custom Sites

### Add Custom Site via CLI

```bash
python main.py
# Select: 1.6 — Add a new site
# Enter: MyStore, https://mystore.com, USD
```

### Programmatically Add

```python
from src.scrapers.factory import add_custom_site

key = add_custom_site(
    name="MyStore",
    url="https://mystore.com",
    currency="USD"
)
print(f"Site registered as: {key}")  # "mystore"
```

### Load on Startup

```python
# main.py
from src.scrapers.factory import load_saved_custom_sites

def main():
    load_saved_custom_sites()  # Auto-load user's custom sites
    # ... rest of app
```

---

## 🔍 Best Practices

### 1. Request Delays

Respect servers — don't hammer them:

```python
def search_products(self, query: str, pages: int = 5) -> SearchResult:
    products = []
    for page in range(1, pages + 1):
        # Delays are built into self._fetch()
        response = self._fetch(url)
        products.extend(self._parse_product(response))
    
    return SearchResult(products, total_products=len(products))
```

### 2. Error Handling

Always handle failures gracefully:

```python
def get_product(self, product_id: str) -> Product | None:
    try:
        response = self._fetch(f"{self.base_url}/product/{product_id}")
        if response:
            return self._parse_product(response)
    except Exception as e:
        logger.error(f"Failed to fetch product {product_id}: {e}")
    
    return None
```

### 3. Type Hints

Always use type hints for clarity:

```python
def search_products(self, query: str, pages: int = 5) -> SearchResult:
    """..."""
    pass

def _parse_product(self, raw_data: dict) -> Product:
    """..."""
    pass
```

### 4. Docstrings

Document your methods with Google-style docstrings:

```python
def search_products(self, query: str, pages: int = 5) -> SearchResult:
    """
    Search for products on this platform.
    
    Args:
        query: Search term (e.g., "laptop")
        pages: Number of pages to scrape (default: 5)
    
    Returns:
        SearchResult with list of products and total count
    
    Raises:
        ConnectionError: If cannot reach the site
        ValueError: If query is empty
    
    Example:
        >>> scraper = MySiteScraper(http_client)
        >>> result = scraper.search_products("laptop", pages=3)
        >>> for product in result.products:
        ...     print(product.title, product.price_current)
    """
```

### 5. Logging

Log important events:

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MySiteScraper(BaseScraper):
    def search_products(self, query: str, pages: int = 5) -> SearchResult:
        logger.info(f"Searching {self.source} for '{query}' ({pages} pages)")
        
        try:
            # ... scraping logic
            logger.info(f"Found {result.total_products} products")
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
        
        return result
```

---

## 📞 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Scraper not found" | Check registry in factory.py, ensure site is registered |
| "Import Error" | Ensure you added `from` statements in factory.py |
| Slow scraping | Check delays in config/settings.py, reduce if needed |
| "Connection refused" | Check if target website is accessible, verify URL |
| No data returned | Check target site structure changed, update parsing logic |

---

## 📚 Related Documentation

- [Base Scraper API](base.py) — Detailed method docs
- [Factory Registry](factory.py) — How sites are managed
- [Models](../models/product.py) — Product data structure
- [Pipeline](../pipeline/cleaner.py) — Data cleaning
- [Root README](../../README.md) — Adding new platforms

---

**Created by:** Mohamed Darwish  
**Last Updated:** 2026-03-29
