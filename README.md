# M-D E-Commerce Scraper

A CMD-based web scraping system that collects structured product data from multiple e-commerce platforms and exports datasets in CSV, Excel, and JSON.

## Platforms
- Amazon (Simulated)
- Noon (Simulated)
- AliExpress (Simulated)
- Jumia (Simulated)
- eBay (Simulated)

## Quickstart
```bash
pip install -r requirements.txt
python main.py
```

## CLI Reference
```bash
# Interactive mode
python main.py

# Scraping
python main.py scrape amazon 10
python main.py scrape all 10 -f csv

# Data
python main.py analyze
python main.py stats
python main.py export csv
```

## Project Structure
- `main.py`: Entry point
- `config/`: Settings
- `src/scrapers/`: Scraper implementations
- `src/models/`: Data models
- `src/pipeline/`: Data cleaning
- `src/storage/`: Database and exports
- `src/analysis/`: Data analysis
- `src/utils/`: Utilities (Colors, Helpers, Logger, HTTP)
