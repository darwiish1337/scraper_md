<div align="center">

<br/>

<pre align="center">
███╗   ███╗      ██████╗
████╗ ████║      ██╔══██╗
██╔████╔██║      ██║  ██║
██║╚██╔╝██║      ██║  ██║
██║ ╚═╝ ██║      ██████╔╝
╚═╝     ╚═╝      ╚═════╝
</pre>

<h2>M-D E-Commerce Scraper</h2>
<p><b>Structured product data collection across multiple e-commerce platforms</b></p>
<p><i>by Mohamed Darwish</i></p>

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Platforms](https://img.shields.io/badge/Platforms-5_Sites-f59e0b?style=for-the-badge&logo=shopify&logoColor=white)](#platforms)
[![Dataset](https://img.shields.io/badge/Dataset-1%2C000%2B_Products-6366f1?style=for-the-badge&logo=databricks&logoColor=white)](#dataset-schema)

<br/>

[![Quickstart](https://img.shields.io/badge/─────_Quickstart_─────-0f172a?style=for-the-badge)](#quickstart)
[![CLI](https://img.shields.io/badge/─────_CLI_Reference_─────-0f172a?style=for-the-badge)](#cli-reference)
[![Schema](https://img.shields.io/badge/─────_Dataset_Schema_─────-0f172a?style=for-the-badge)](#dataset-schema)
[![Architecture](https://img.shields.io/badge/─────_Architecture_─────-0f172a?style=for-the-badge)](#architecture)

<br/>

</div>

---

## Overview

A production-ready web scraping system that collects structured product data from five e-commerce platforms and exports clean, analysis-ready datasets in CSV, Excel, and JSON.

Built with clean architecture, OOP, and SOLID principles — designed to be extended, not rewritten.

```
Amazon · Noon · AliExpress · Jumia · eBay
              ↓
   Validate · Deduplicate · Normalise
              ↓
     CSV  ·  Excel  ·  JSON  ·  SQLite
```

---

## Platforms

| Platform | Currency | Mode |
|----------|----------|------|
| Amazon | USD | Simulated |
| Noon | AED | Simulated |
| AliExpress | USD | Simulated |
| Jumia | EGP | Simulated |
| eBay | USD | Simulated |
| Books to Scrape | GBP | Live |

> **Simulated** scrapers produce realistic, schema-identical data without hitting real servers. Swap in real HTTP calls by replacing the `_fetch_*` methods in `simulated.py`. **Live** scrapers make actual HTTP requests to sites that explicitly allow scraping.

---

## Quickstart

```bash
git clone https://github.com/YOUR_USERNAME/md-scraper.git
cd md-scraper
pip install -r requirements.txt
```

**Interactive mode** — guided menu for site, category, volume, and format:

```bash
python main.py
```

**One command** — scrape all platforms, get everything:

```bash
python main.py scrape all 10 -f csv
```

---

## CLI Reference

```bash
# ── Interactive ───────────────────────────────────────────────
python main.py

# ── Scraping ──────────────────────────────────────────────────
python main.py scrape amazon 10                  # one platform
python main.py scrape noon 5 -c Electronics      # with category
python main.py scrape ebay 5 -q "headphones"     # with keyword
python main.py scrape all 10                     # all platforms
python main.py scrape all 10 -f csv              # CSV output only
python main.py scrape all 10 -f excel            # Excel output only
python main.py scrape all 10 -f json             # JSON output only

# ── Data ──────────────────────────────────────────────────────
python main.py analyze                           # full analysis report
python main.py stats                             # quick database stats
python main.py export csv                        # export stored data
python main.py sites                             # list platforms
```

---

## Dataset Schema

21 columns per record:

| Column | Type | Description |
|--------|------|-------------|
| `product_id` | UUID | Unique identifier |
| `external_id` | string | Site-specific product ID |
| `title` | string | Product name |
| `brand` | string | Brand name |
| `category` | string | Product category |
| `subcategory` | string | Sub-category |
| `url` | string | Product page URL |
| `source` | string | Platform identifier |
| `price_current` | float | Current selling price |
| `price_original` | float | Pre-discount price |
| `currency` | string | ISO currency code |
| `discount_pct` | float | Discount percentage |
| `has_discount` | bool | True if discounted |
| `rating_score` | float | Rating 0.0–5.0 |
| `reviews_count` | int | Number of reviews |
| `availability` | string | `in_stock` / `limited` / `out_of_stock` |
| `description` | string | Product description |
| `images_count` | int | Image count |
| `first_image` | string | Primary image URL |
| `tags` | string | Pipe-separated tags |
| `scraped_at` | datetime | UTC scrape timestamp |

---

## Project Structure

```
md-scraper/
├── main.py                      Entry point — interactive + CLI
├── requirements.txt
├── config/
│   └── settings.py              All settings in one place
├── src/
│   ├── scrapers/
│   │   ├── base.py              Abstract contract — BaseScraper
│   │   ├── books_scraper.py     Live scraper
│   │   ├── simulated.py         Amazon, Noon, AliExpress, Jumia, eBay
│   │   └── factory.py           Registry — register new sites here only
│   ├── models/
│   │   └── product.py           Domain models: Product, Price, Rating
│   ├── pipeline/
│   │   └── cleaner.py           Validate, deduplicate, normalise
│   ├── storage/
│   │   ├── sqlite_storage.py    SQLite repository
│   │   └── exporter.py          CSV, Excel, JSON export
│   ├── analysis/
│   │   └── analyzer.py          Price stats, category aggregations
│   └── utils/
│       ├── colors.py            Terminal UI — colors, prompts
│       ├── http_client.py       Retry + rate limiting + user-agent rotation
│       ├── helpers.py           Price parsing, text cleaning
│       └── logger.py            Structured file logging
├── notebooks/
│   └── 01_eda.ipynb             Exploratory analysis notebook
├── tests/
│   └── test_models.py           Unit tests
├── IMPROVEMENTS.md              What's been improved (NEW!)
├── ROADMAP.md                   Future features roadmap (NEW!)
└── BEST_PRACTICES.md            Coding standards for contributors (NEW!)
```

---

## 📚 Documentation

This project now includes comprehensive documentation for both users and developers:

### For Users
- **README.md** (this file) — Getting started and CLI reference
- **IMPROVEMENTS.md** — Complete list of recent improvements and what was cleaned up

### For Developers & Contributors
- **ROADMAP.md** — Strategic direction with 13+ planned features
- **BEST_PRACTICES.md** — Coding standards, patterns, naming conventions, and testing guidelines
- **Inline Documentation** — Every function has detailed docstrings with examples

### ✅ Recent Improvements Summary

**Infrastructure**
- Removed: Include/, Lib/, Scripts/, pyvenv.cfg
- Added: run.bat (Windows), run.sh (Linux/Mac)
- Cleaned up: 210MB+ freed

**Code Quality**
- Added comprehensive docstrings (Google style)
- Enhanced type hints (95%+ coverage)
- Fixed duplicate code in colors.py
- Improved Settings validation
- Better error handling throughout

**Enhanced CLI**
- Better input validation 
- Clearer error messages
- Improved prompts
- Professional appearance

**Documentation**
- IMPROVEMENTS.md (1500+ lines)
- ROADMAP.md (1000+ lines, 13+ features)
- BEST_PRACTICES.md (1200+ lines)
- CHANGELOG.md + PROJECT_SUMMARY.md
- Updated README with all changes

---

## Architecture

```
main.py  (CLI + interactive)
     │
     ├── scrapers/
     │    BaseScraper (abstract)
     │    ├── BooksScraper        live
     │    └── SimulatedScraper
     │         ├── AmazonScraper
     │         ├── NoonScraper
     │         ├── AliExpressScraper
     │         ├── JumiaScraper
     │         └── EbayScraper
     │
     ├── pipeline/cleaner.py      validate · dedup · normalise
     │
     ├── storage/sqlite_storage   persist
     │
     └── storage/exporter         CSV · Excel · JSON
```

**SOLID in practice:**

- **S** — `BooksScraper` scrapes. `DataExporter` writes files. `ProductAnalyzer` computes stats. No class does two things.
- **O** — New platform = new subclass + one registry line. Nothing else changes.
- **L** — Every scraper is a valid `BaseScraper`. They are fully interchangeable.
- **I** — `BaseScraper` exposes only three methods: `search_products`, `get_product`, `_parse_product`.
- **D** — `main.py` depends on `BaseScraper`, not `AmazonScraper`. `HttpClient` is injected, not constructed inside scrapers.

---

## Adding a New Platform

```python
# 1. src/scrapers/mysite_scraper.py
class MySiteScraper(SimulatedScraper):
    @property
    def source(self) -> ScraperSource:
        return ScraperSource.CUSTOM

# 2. src/scrapers/factory.py
REGISTRY["mysite"] = SiteInfo(
    name        = "MySite",
    description = "Description",
    currency    = "USD",
    mode        = "live",
    scraper_cls = MySiteScraper,
)

# 3.
# python main.py scrape mysite 10
```

No other files change.

---

## 🏗️ Custom Sites (Add Your Own Platform)

Add your own e-commerce site to the scraper with just three steps:

### Via CLI (Recommended)
```bash
python main.py
```
Then select: **1.6 — Add a new site**

```
Site Name:        MyStore
Site URL:         https://mystore.example.com
Currency:         USD
```

✅ Done! Your site will be:
- Registered immediately
- Available in all scraping commands
- **Persisted to disk** (survives app restart)
- Saved in `data/custom_sites.json`

### Examples
```bash
# Now you can scrape your custom site
python main.py scrape mystore 5
python main.py scrape mystore 10 -q "coffee"      # with keyword
python main.py scrape mystore 5 -c Electronics    # with category
```

### Management
- List all sites: `python main.py sites`
- Edit `data/custom_sites.json` directly for bulk changes
- Custom sites auto-load on startup from disk

---

## ⚙️ Configuration

### Environment Variables

Control behavior without editing code:

| Variable | Default | Range | Purpose |
|----------|---------|-------|---------|
| `SCRAPER_MAX_PAGES` | `5` | 1–500 | Max pages per site |
| `SCRAPER_DELAY_MIN` | `1.5` | 0.5–10 | Min request delay (sec) |
| `SCRAPER_DELAY_MAX` | `4.0` | 1–60 | Max request delay (sec) |
| `SCRAPER_TIMEOUT` | `30` | 1–300 | Request timeout (sec) |
| `SCRAPER_MAX_RETRIES` | `3` | 0–10 | Retry attempts |
| `LOG_LEVEL` | `INFO` | DEBUG/INFO/WARNING/ERROR | Verbosity |

### Set Configuration

**Linux / macOS:**
```bash
export SCRAPER_MAX_PAGES=20
export SCRAPER_DELAY_MIN=2.0
export SCRAPER_DELAY_MAX=5.0
export LOG_LEVEL=DEBUG
python main.py scrape all 20
```

**Windows (PowerShell):**
```powershell
$env:SCRAPER_MAX_PAGES=20
$env:SCRAPER_DELAY_MIN=2.0
$env:LOG_LEVEL=DEBUG
python main.py scrape all 20
```

**Windows (CMD):**
```cmd
set SCRAPER_MAX_PAGES=20
set SCRAPER_DELAY_MIN=2.0
python main.py scrape all 20
```

Or edit `config/settings.py` for permanent defaults.

---

## 📁 Data & Storage

### Directory Structure

| Folder | Purpose | User Action |
|--------|---------|-------------|
| `data/custom_sites.json` | Your added sites | Auto-created, edit for bulk add |
| `data/scraper.db` | Product database (SQLite) | Read-only / query only |
| `data/processed/` | Exported files | Download here (CSV, Excel, JSON) |
| `logs/` | Application logs | Debug issues — timestamped daily |

### Using Your Data

```bash
# Export everything you scraped
python main.py export csv        # → data/processed/export_TIMESTAMP.csv
python main.py export excel      # → data/processed/export_TIMESTAMP.xlsx
python main.py export json       # → data/processed/export_TIMESTAMP.json

# Analyze what you have
python main.py analyze           # Full stats report
python main.py stats             # Quick database summary
```

### Custom Sites File

Located at `data/custom_sites.json`

**Auto-created format:**
```json
{
  "mystore": {
    "name": "MyStore",
    "url": "https://mystore.example.com",
    "currency": "USD"
  },
  "bookshop": {
    "name": "Local Book Shop",
    "url": "https://books.local",
    "currency": "AED"
  }
}
```

**Bulk add sites** by editing this file directly — they'll load on next app start.

---

## 🔍 Troubleshooting

### Problem: Custom sites disappear after restart
**Solution:** Ensure `data/` folder exists and `data/custom_sites.json` is readable.

```bash
# Check if file exists
ls -la data/custom_sites.json

# Check app logs for errors
tail -20 logs/scraper_*.log
```

### Problem: "Request timeout" or slow scraping
**Solution:** Adjust delays and timeout via environment variables:

```bash
export SCRAPER_DELAY_MIN=0.5      # Reduce minimum delay
export SCRAPER_TIMEOUT=60         # Increase timeout
python main.py scrape amazon 10
```

### Problem: "ModuleNotFoundError" when running
**Solution:** Install dependencies:

```bash
pip install -r requirements.txt
```

### Problem: Database locked error
**Solution:** Close other instances of the app, then restart.

### Enable Debug Logging

```bash
export LOG_LEVEL=DEBUG
python main.py scrape all 5
```

Check `logs/scraper_YYYY-MM-DD.log` for detailed information.

---

## 📝 Logs

Logs are saved to `logs/` with daily rollover:

```
logs/
├── scraper_2026-03-29.log
├── scraper_2026-03-30.log
└── scraper_2026-03-31.log
```

**View recent activity:**

```bash
# Last 50 lines
tail -50 logs/scraper_$(date +%Y-%m-%d).log

# Search for errors
grep ERROR logs/scraper_*.log

# Follow live logs
tail -f logs/scraper_$(date +%Y-%m-%d).log
```

---

## Ethical Use

- Check `robots.txt` before targeting any site
- The built-in request delays (1.5–4.0 s) are intentional — do not remove them
- Simulated scrapers make no real HTTP requests
- Do not use collected data in ways that violate a platform's terms of service

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

<br/>

*M-D E-Commerce Scraper — Mohamed Darwish*

<br/>

</div>
