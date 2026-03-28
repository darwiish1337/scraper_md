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

---

A production-ready web scraping system for collecting structured product data from multiple e-commerce platforms. Built with Python, clean architecture, OOP, and SOLID principles.

Ships with **1,000+ products** across 5 platforms and 10 categories, ready to upload to Kaggle.

---

## Supported Platforms

| Platform | Currency | Mode | Products / Page |
|----------|----------|------|-----------------|
| Amazon | USD | Simulated | 20 |
| Noon | AED | Simulated | 20 |
| AliExpress | USD | Simulated | 20 |
| Jumia | EGP | Simulated | 20 |
| eBay | USD | Simulated | 20 |
| Books to Scrape | GBP | Live | 20 |

> **Simulated** scrapers generate realistic, schema-identical data. The Books scraper hits a real site built for scraping practice. Replace `simulated.py`'s `_fetch_*` methods with real HTTP calls to go fully live on any platform.

---

## Quickstart

The easiest way to get started on Windows:

1. **Setup**: Run `setup.bat` to create the virtual environment and install all dependencies automatically.
2. **Run**: Run `run.bat` to launch the interactive scraper with the branded red UI.

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/md-scraper.git
cd md-scraper
pip install -r requirements.txt
```

### Interactive mode (recommended)

```bash
python main.py
```

You will be guided through site selection, category filtering, page count, and export format — with a colored interactive menu.

### Direct commands

```bash
# Scrape one site
python main.py scrape amazon 10

# Scrape with category filter
python main.py scrape noon 5 -c Electronics

# Scrape with keyword
python main.py scrape ebay 5 -q "wireless headphones"

# Scrape all sites
python main.py scrape all 5

# Scrape all, export as CSV only
python main.py scrape all 10 -f csv

# Analyze stored data
python main.py analyze

# Export existing database to Excel
python main.py export excel

# Quick stats
python main.py stats

# List available sites
python main.py sites
```

---

## Dataset Schema

Every scraped product includes the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `product_id` | UUID | Unique identifier |
| `external_id` | string | Site-specific product ID |
| `title` | string | Product name |
| `brand` | string | Brand name |
| `category` | string | Product category |
| `subcategory` | string | Sub-category (when available) |
| `url` | string | Product page URL |
| `source` | string | Platform identifier |
| `price_current` | float | Current selling price |
| `price_original` | float | Original price before discount |
| `currency` | string | ISO currency code |
| `discount_pct` | float | Discount percentage |
| `has_discount` | bool | True if discounted |
| `rating_score` | float | Rating 0.0 – 5.0 |
| `reviews_count` | int | Number of customer reviews |
| `availability` | string | `in_stock` / `limited` / `out_of_stock` |
| `description` | string | Product description |
| `images_count` | int | Number of product images |
| `first_image` | string | Primary image URL |
| `tags` | string | Pipe-separated tags |
| `scraped_at` | datetime | UTC scrape timestamp |

---

## Project Structure

```
md-scraper/
├── main.py                          Entry point — interactive + CLI
├── requirements.txt
├── config/
│   └── settings.py                  All configuration in one place
├── src/
│   ├── scrapers/
│   │   ├── base.py                  Abstract scraper contract (SOLID)
│   │   ├── books_scraper.py         Live scraper — books.toscrape.com
│   │   ├── simulated.py             Amazon, Noon, AliExpress, Jumia, eBay
│   │   └── factory.py               Scraper factory + site registry
│   ├── models/
│   │   └── product.py               Domain models: Product, Price, Rating
│   ├── pipeline/
│   │   └── cleaner.py               Validation, deduplication, normalisation
│   ├── storage/
│   │   ├── sqlite_storage.py        SQLite repository
│   │   └── exporter.py              CSV, Excel, JSON export
│   ├── analysis/
│   │   └── analyzer.py              Price stats, category aggregations
│   └── utils/
│       ├── colors.py                Terminal color engine + UI prompts
│       ├── http_client.py           Anti-detection HTTP client with retry
│       ├── helpers.py               Price parsing, text cleaning
│       └── logger.py                File-based structured logging
├── data/
│   └── processed/                   Exported datasets (CSV, Excel, JSON)
├── notebooks/
│   └── 01_eda.ipynb                 EDA notebook for Kaggle
└── tests/
    └── test_models.py               Unit tests
```

---

## Architecture

```
CLI (main.py)
     │
     ▼
Scrapers  ─── BaseScraper (abstract)
               ├── BooksScraper   (live)
               └── SimulatedScraper
                    ├── AmazonScraper
                    ├── NoonScraper
                    ├── AliExpressScraper
                    ├── JumiaScraper
                    └── EbayScraper
     │
     ▼
Pipeline  ─── cleaner.py (validate, dedup, normalise)
     │
     ▼
Storage   ─── SQLiteStorage (persist + history)
     │
     ▼
Exporter  ─── CSV / Excel / JSON
```

### SOLID principles applied

- **S** — Each class has one reason to change. `BooksScraper` scrapes. `DataExporter` writes files. `ProductAnalyzer` computes stats.
- **O** — Add a new site by subclassing `BaseScraper` and registering in `factory.py`. Nothing else changes.
- **L** — All scrapers are interchangeable wherever `BaseScraper` is expected.
- **I** — `BaseScraper` exposes only `search_products`, `get_product`, `_parse_product`.
- **D** — `main.py` depends on `BaseScraper`, not on `AmazonScraper`. `HttpClient` is injected, not constructed inside scrapers.

---

## Adding a New Site

1. Create `src/scrapers/mysite_scraper.py` and subclass `BaseScraper` (or `SimulatedScraper`)
2. Implement `source`, `base_url`, `search_products`, `get_product`, `_parse_product`
3. Register in `src/scrapers/factory.py`:

```python
REGISTRY["mysite"] = SiteInfo(
    name        = "MySite",
    description = "Description of the site",
    currency    = "USD",
    mode        = "live",
    scraper_cls = MySiteScraper,
)
```

4. Run: `python main.py scrape mysite 5`

No other files change.

---

## Configuration

Override any setting via environment variable:

```bash
export SCRAPER_MAX_PAGES=20
export SCRAPER_DELAY_MIN=2.0
export SCRAPER_DELAY_MAX=5.0
export LOG_LEVEL=DEBUG
python main.py scrape all 20
```

---

## Uploading to Kaggle

1. Run `python main.py scrape all 10 -f csv`
2. Find the CSV in `data/processed/`
3. Go to [kaggle.com/datasets/new](https://www.kaggle.com/datasets/new)
4. Upload the CSV
5. Use `notebooks/01_eda.ipynb` as the starter notebook

Suggested tags: `e-commerce`, `prices`, `web scraping`, `retail`, `multi-platform`, `classification`, `regression`

---

## Ethical Use

- Always check `robots.txt` before targeting any site
- The built-in delays (1.5 – 4.0 s between requests) are intentional — do not remove them
- Do not use scraped data for spam, resale, or any purpose that violates a site's terms of service
- The simulated scrapers generate synthetic data and make no real HTTP requests

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

*M-D Web Scraper — Mohamed Darwish*

</div>
