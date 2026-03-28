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
![Platforms](https://img.shields.io/badge/Platforms-Dynamic-f59e0b?style=flat-square)
![Products](https://img.shields.io/badge/Dataset-1%2C000%2B_products-6366f1?style=flat-square)
![Architecture](https://img.shields.io/badge/Architecture-Clean_+_SOLID-0ea5e9?style=flat-square)

<br/>

[Quickstart](#quickstart) · [Platforms](#platforms) · [Features](#key-features) · [CLI](#cli-reference) · [Schema](#dataset-schema)

<br/>

</div>

---

## What it does

Collects structured product data from multiple e-commerce platforms and exports clean, analysis-ready datasets in CSV, Excel, and JSON. Built for data scientists, analysts, and developers who want real-world e-commerce data with a professional CLI experience.

```
Amazon · Noon · AliExpress · Jumia · eBay · + Custom Sites  →  CSV / Excel / JSON
```

---

## Quickstart

The easiest way to get started on Windows:

1. **Setup**: Run `setup.bat` to create the virtual environment and install all dependencies automatically.
2. **Run**: Run `run.bat` to launch the interactive scraper with the branded red UI.

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/md-scraper.git
cd md-scraper

# One-click setup (Windows)
setup.bat

# One-click run (Windows)
run.bat
```

---

## Key Features

- **🔴 Professional CLI**: Red centered ASCII logo with a clean, interactive interface.
- **🔄 Dynamic Site Addition**: Add any new e-commerce site directly through the CLI during your session.
- **💸 Currency Selection**: Choose your preferred output currency (USD, EGP, AED, SAR) before scraping.
- **🔙 Easy Navigation**: "Back" options in all menus for a smooth interactive experience.
- **🧹 Data Management**: Built-in option to "Clean Current Data" to reset your local database.
- **📊 Integrated Analysis**: Instant price statistics and category breakdowns after every run.

---

## Platforms

| Platform | Default Currency | Mode |
|----------|------------------|------|
| Amazon | USD | Simulated |
| Noon | AED | Simulated |
| AliExpress | USD | Simulated |
| Jumia | EGP | Simulated |
| eBay | USD | Simulated |
| **+ Add Your Own** | *User Defined* | Dynamic |

---

## CLI Reference

```bash
# Interactive guided session (Recommended)
run.bat  # Or: .\Scripts\python main.py

# Direct Scrape Commands
.\Scripts\python main.py scrape amazon 10
.\Scripts\python main.py scrape all 5 -f csv

# Management & Analysis
.\Scripts\python main.py analyze    # Detailed data analysis
.\Scripts\python main.py stats      # Quick database summary
.\Scripts\python main.py export csv # Export existing data
```

---

## Dataset Schema

Every product record includes:

| Column | Description |
|--------|-------------|
| `product_id` | Unique UUID |
| `title` | Product name |
| `brand` | Manufacturer |
| `category` | Product category |
| `price_current`| Current price |
| `currency` | Selected currency |
| `discount_pct` | % off |
| `availability` | stock status |
| `scraped_at` | UTC timestamp |

---

## Project Structure

```
main.py                # Entry point (CLI + Interactive)
run.bat / setup.bat    # Windows automation scripts
src/
├── scrapers/          # Scraper logic & Factory
├── pipeline/          # Data cleaning & validation
├── storage/           # SQLite & Exporter logic
├── analysis/          # Data processing & stats
└── utils/             # UI, Logger, & HTTP client
data/
└── processed/         # Exported CSV/Excel/JSON files
```

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

*M-D Web Scraper — Mohamed Darwish*

</div>
