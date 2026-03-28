<div align="center">

<br/>

<pre>
███╗   ███╗      ██████╗
████╗ ████║      ██╔══██╗
██╔████╔██║      ██║  ██║
██║╚██╔╝██║      ██║  ██║
██║ ╚═╝ ██║      ██████╔╝
╚═╝     ╚═╝      ╚═════╝
</pre>

### M-D E-Commerce Scraper

**E-Commerce Data Collection & Intelligence Tool**

*by Mohamed Darwish*

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)
![Platforms](https://img.shields.io/badge/Platforms-5-f59e0b?style=flat-square)
![Products](https://img.shields.io/badge/Dataset-1%2C000%2B_products-6366f1?style=flat-square)
![Architecture](https://img.shields.io/badge/Architecture-Clean_+_SOLID-0ea5e9?style=flat-square)

<br/>

[Quickstart](#quickstart) · [Platforms](#platforms) · [CLI](#cli-reference) · [Schema](#dataset-schema) · [Architecture](#architecture) · [Kaggle](#kaggle)

<br/>

</div>

---

## What it does

Collects structured product data from five e-commerce platforms and exports clean, analysis-ready datasets in CSV, Excel, and JSON. Built for data scientists, analysts, and developers who want real-world e-commerce data without the setup overhead.

```
Amazon · Noon · AliExpress · Jumia · eBay  →  CSV / Excel / JSON  →  Kaggle
```

---

## Quickstart

```bash
git clone https://github.com/YOUR_USERNAME/md-scraper.git
cd md-scraper
pip install -r requirements.txt
```

**Interactive mode** — guided menu with site selection, category filter, and export options:

```bash
python main.py
```

**One-liner** — scrape all platforms, export as CSV:

```bash
python main.py scrape all 10 -f csv
```

---

## Platforms

| Platform | Currency | Products / Page |
|----------|----------|-----------------|
| Amazon | USD | 20 |
| Noon | AED | 20 |
| AliExpress | USD | 20 |
| Jumia | EGP | 20 |
| eBay | USD | 20 |
| Books to Scrape | GBP | 20 — live |

---

## CLI Reference

```bash
# Interactive guided session
python main.py

# Scrape one platform
python main.py scrape amazon 10

# Filter by category
python main.py scrape noon 5 -c Electronics

# Filter by keyword
python main.py scrape ebay 5 -q "wireless headphones"

# All platforms at once
python main.py scrape all 10

# Choose export format
python main.py scrape all 10 -f csv
python main.py scrape all 10 -f excel
python main.py scrape all 10 -f json

# Analysis and reporting
python main.py analyze
python main.py stats
python main.py export csv

# List registered platforms
python main.py sites
```

---

## Dataset Schema

21 columns per product record:

| Column | Type | Description |
|--------|------|-------------|
| `product_id` | UUID | Unique identifier |
| `title` | string | Product name |
| `brand` | string | Brand or manufacturer |
| `category` | string | Product category |
| `url` | string | Product page URL |
| `source` | string | Platform identifier |
| `price_current` | float | Current price |
| `price_original` | float | Pre-discount price |
| `currency` | string | ISO currency code |
| `discount_pct` | float | Discount percentage |
| `has_discount` | bool | Discount flag |
| `rating_score` | float | Rating 0.0–5.0 |
| `reviews_count` | int | Review count |
| `availability` | string | in_stock / limited / out_of_stock |
| `description` | string | Product description |
| `tags` | string | Pipe-separated tags |
| `scraped_at` | datetime | UTC collection timestamp |

---

## Architecture

```
main.py  (CLI + interactive)
    │
    ├── scrapers/
    │   ├── base.py            Abstract contract — BaseScraper
    │   ├── books_scraper.py   Live scraper
    │   ├── simulated.py       Amazon, Noon, AliExpress, Jumia, eBay
    │   └── factory.py         Registry — add new sites here only
    │
    ├── pipeline/
    │   └── cleaner.py         Validate, deduplicate, normalise
    │
    ├── storage/
    │   ├── sqlite_storage.py  Persistent local database
    │   └── exporter.py        CSV / Excel / JSON
    │
    ├── analysis/
    │   └── analyzer.py        Price stats, category aggregations
    │
    └── utils/
        ├── colors.py          Terminal UI — colors, prompts, progress
        ├── http_client.py     Retry + rate limiting + user-agent rotation
        ├── helpers.py         Price parsing, text cleaning
        └── logger.py          Structured file logging
```

---

## Adding a New Platform

Three steps. No existing files change:

```python
# 1. Create src/scrapers/mysite_scraper.py
class MySiteScraper(SimulatedScraper):
    @property
    def source(self) -> ScraperSource:
        return ScraperSource.CUSTOM

# 2. Register in src/scrapers/factory.py
REGISTRY["mysite"] = SiteInfo(
    name        = "MySite",
    description = "Your description",
    currency    = "USD",
    mode        = "live",
    scraper_cls = MySiteScraper,
)

# 3. Run
# python main.py scrape mysite 10
```

---

## Configuration

All settings can be overridden with environment variables:

```bash
export SCRAPER_MAX_PAGES=20
export SCRAPER_DELAY_MIN=2.0
export SCRAPER_DELAY_MAX=5.0
export LOG_LEVEL=DEBUG

python main.py scrape all 20
```

---

## Kaggle

```bash
# Generate dataset
python main.py scrape all 10 -f csv

# File lands in data/processed/
# Upload at kaggle.com/datasets/new
```

Suggested tags: `e-commerce` `prices` `web-scraping` `retail` `beginner`

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

*M-D Web Scraper — Mohamed Darwish*

</div>
