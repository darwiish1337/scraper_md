<div align="center">

<br/>

<pre align="center">
  __  __      _____
 |  \/  |    |  __ \
 | \  / |    | |  | |
 | |\/| |    | |  | |
 | |  | |    | |__| |
 |_|  |_|    |_____/
</pre>

<h2>M-D E-Commerce Scraper</h2>
<p><b>A modern, high-volume structured product data collection system</b></p>
<p><i>Inspired by the Claude Code CLI experience</i></p>

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Platforms](https://img.shields.io/badge/Platforms-5_Sites-ff8a65?style=for-the-badge&logo=shopify&logoColor=white)](#platforms)
[![Capacity](https://img.shields.io/badge/Capacity-20%2C000+_Products-ff8a65?style=for-the-badge&logo=databricks&logoColor=white)](#overview)

<br/>

[![Quickstart](https://img.shields.io/badge/─────_Quickstart_─────-0f172a?style=for-the-badge)](#quickstart)
[![CLI](https://img.shields.io/badge/─────_CLI_Reference_─────-0f172a?style=for-the-badge)](#cli-usage)
[![Architecture](https://img.shields.io/badge/─────_Architecture_─────-0f172a?style=for-the-badge)](#project-structure)

<br/>

</div>

---

## 🚀 Overview

A production-ready CLI scraping system built with Python. It collects, cleans, and stores product data from multiple e-commerce platforms, providing analysis-ready datasets in multiple formats.

- **Multi-Platform:** Amazon, Noon, AliExpress, Jumia, and eBay.
- **High Volume:** Support for up to **1000 pages per site** (~20,000 products).
- **Modern UI:** Minimalist "Claude Code" inspired CLI with a clean Peach-theme.
- **Clean Data:** Automatic validation, deduplication, and normalization.

---

## 📦 Platforms

| Platform | Currency | Mode | Status |
|----------|----------|------|--------|
| **Amazon** | USD | Simulated | ✅ Ready |
| **Noon** | AED | Simulated | ✅ Ready |
| **AliExpress** | USD | Simulated | ✅ Ready |
| **Jumia** | EGP | Simulated | ✅ Ready |
| **eBay** | USD | Simulated | ✅ Ready |
| **Books to Scrape** | GBP | Live | ✅ Ready |

---

## ⚡ Quickstart

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Interactive Mode (Recommended):**
   ```bash
   python main.py
   ```

3. **Or use direct commands:**
   ```bash
   # Scrape 10 pages from Amazon
   python main.py scrape amazon 10
   ```

---

## 💻 CLI Usage

### 🔍 Scraping
```bash
python main.py scrape all 5              # Scrape all sites (5 pages each)
python main.py scrape noon 10 -q "phone" # Scrape specific site with keyword
python main.py scrape ebay 5 -f csv      # Scrape and export to CSV directly
```

### 📊 Data & Analysis
```bash
python main.py analyze                   # Show full analysis report
python main.py stats                     # Show quick database statistics
python main.py sites                     # List all available platforms
```

### 📂 Exporting
```bash
python main.py export csv                # Export all stored data to CSV
python main.py export excel              # Export to Excel format
```

---

## 📁 Project Structure

```text
md-scraper/
├── main.py              # Entry point (CLI + Interactive)
├── config/              # Configuration & Settings
├── src/
│   ├── scrapers/        # Scraping logic for all sites
│   ├── models/          # Data structures (Product, Price)
│   ├── pipeline/        # Cleaning & Normalization
│   ├── storage/         # Database & Exporters
│   └── utils/           # Colors, HTTP Client, Logger
├── data/                # Database & Exported files
└── logs/                # Application logs
```

---

## ⚙️ Configuration

Control the scraper behavior using environment variables or [settings.py](file:///c:/Users/PC\Desktop\scraper_md\config\settings.py):

| Variable | Default | Purpose |
|----------|---------|---------|
| `SCRAPER_MAX_PAGES` | `1000` | Maximum pages per site |
| `SCRAPER_DELAY_MIN` | `1.5` | Minimum delay between requests |
| `SCRAPER_TIMEOUT` | `30` | Request timeout in seconds |
| `LOG_LEVEL` | `INFO` | Verbosity (DEBUG/INFO/ERROR) |

---

## 💾 Data & Storage

- **Database:** All scraped data is stored in `data/scraper.db` (SQLite).
- **Exports:** Found in `data/processed/`.
- **Custom Sites:** Add your own sites via the interactive menu; they are saved in `data/custom_sites.json`.

---

## 📖 Documentation

For more detailed information, check the module-specific documentation:
- [Developer Guidelines](file:///c:/Users/PC/Desktop/scraper_md/BEST_PRACTICES.md)
- [Source Code Structure](file:///c:/Users/PC/Desktop/scraper_md/src/README.md)
- [Scraper Development](file:///c:/Users/PC/Desktop/scraper_md/src/scrapers/README.md)

---

## ⚖️ License & Ethical Use

- **License:** MIT - See [LICENSE](file:///c:/Users/PC/Desktop/scraper_md/LICENSE) for details.
- **Ethics:** Please respect `robots.txt` and use the built-in delays to avoid overwhelming servers.

<div align="center">
<br/>
<i>M-D E-Commerce Scraper — Mohamed Darwish</i>
<br/>
</div>
