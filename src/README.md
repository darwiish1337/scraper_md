# 🏗️ Source Code (`src/`)

This directory contains the core application logic organized by concerns.

---

## 📁 Structure

```
src/
├── __init__.py                    Module marker
│
├── scrapers/                      🕷️ Web scraping layer
│   ├── base.py                    Abstract base class
│   ├── simulated.py               Simulated scrapers (Amazon, Noon, etc.)
│   ├── books_scraper.py           Live Books to Scrape scraper
│   ├── factory.py                 Registry & scraper creation
│   ├── custom_sites.py            User-added site persistence
│   └── README.md                  → See for adding new platforms
│
├── models/                        📊 Domain models (data structures)
│   ├── product.py                 Product, Price, Rating, SearchResult
│   └── README.md                  → See for model references
│
├── pipeline/                      🔄 Data validation & transformation
│   ├── cleaner.py                 Validate, deduplicate, normalize
│   └── README.md                  → See for data pipeline docs
│
├── storage/                       💾 Persistence layer
│   ├── sqlite_storage.py          SQLite database operations
│   ├── exporter.py                CSV, Excel, JSON export
│   └── README.md                  → See for data export docs
│
├── analysis/                      📈 Analytics & reporting
│   ├── analyzer.py                Price stats, category analysis
│   └── README.md                  → See for analysis docs
│
└── utils/                         🛠️ Utilities (no business logic)
    ├── colors.py                  "Claude Code" UI, dynamic centering, prompts
    ├── http_client.py             HTTP requests with retry logic
    ├── helpers.py                 Price parsing, text cleaning
    ├── logger.py                  Logging setup
    └── README.md                  → See for utility docs
```

---

## 📖 Module Quick Reference

### 🕷️ `scrapers/` — Data Collection

[→ Full docs in scrapers/README.md](scrapers/README.md)

**Responsibilities:**
- Collect product data from e-commerce sites
- Normalize to Product model
- Manage scrapers (registry pattern)

**Key Classes:**
- `BaseScraper` — Abstract contract
- `SimulatedScraper` — Fake data generator
- `BooksScraper` — Live HTTP scraper

**Usage:**
```python
from src.scrapers.factory import create_scraper

scraper = create_scraper('amazon')
result = scraper.search_products('laptop', pages=5)
```

---

### 📊 `models/` — Data Structures

[→ Full docs in models/README.md](models/README.md)

**Responsibilities:**
- Define Product, Price, Rating models
- Validate data structure
- Type safety

**Key Classes:**
- `Product` — Single product with 21 fields
- `Price` — Currency-aware pricing
- `Rating` — Review statistics
- `SearchResult` — Query result wrapper

**Usage:**
```python
from src.models.product import Product

product = Product(
    product_id="abc123",
    title="Laptop",
    price_current=999.99,
    currency="USD",
    source="amazon"
)

# All fields have type hints and validation
print(product.title)         # "Laptop"
print(product.price_current) # 999.99
```

---

### 🔄 `pipeline/` — Data Processing

[→ Full docs in pipeline/README.md](pipeline/README.md)

**Responsibilities:**
- Validate products
- Remove duplicates
- Normalize data (price parsing, text cleaning)

**Key Classes:**
- `DataCleaner` — Main cleaner

**Usage:**
```python
from src.pipeline.cleaner import DataCleaner

cleaner = DataCleaner()
cleaned = cleaner.clean(raw_products)
validated = cleaner.validate_all(products)
```

---

### 💾 `storage/` — Persistence

[→ Full docs in storage/README.md](storage/README.md)

**Responsibilities:**
- Store products in SQLite
- Export to CSV, Excel, JSON
- Query database

**Key Classes:**
- `SQLiteStorage` — Database access
- `DataExporter` — File export (CSV, Excel, JSON)

**Usage:**
```python
from src.storage.sqlite_storage import SQLiteStorage

db = SQLiteStorage()
db.save_products(products)
all_products = db.get_all()

from src.storage.exporter import DataExporter
exporter = DataExporter()
exporter.to_csv("output.csv", products)
```

---

### 📈 `analysis/` — Analytics

[→ Full docs in analysis/README.md](analysis/README.md)

**Responsibilities:**
- Calculate price statistics
- Analyze categories
- Generate reports

**Key Classes:**
- `ProductAnalyzer` — Main analyzer

**Usage:**
```python
from src.analysis.analyzer import ProductAnalyzer

analyzer = ProductAnalyzer()
report = analyzer.generate_report(products)
print(report.avg_price)        # Average price
print(report.category_counts)  # Products per category
```

---

### 🛠️ `utils/` — Helpers

[→ Full docs in utils/README.md](utils/README.md)

**Responsibilities:**
- No business logic
- Support all other modules
- Reusable utilities

**Key Classes:**
- `HttpClient` — Requests with retry + delays
- `Logger` — Structured logging
- `ColoredPrompt` — User prompts with colors

**Usage:**
```python
# HTTP requests
from src.utils.http_client import HttpClient
http = HttpClient()
response = http.get("https://example.com", timeout=30)

# Logging
from src.utils.logger import get_logger
logger = get_logger(__name__)
logger.info("Processing started")

# Colors
from src.utils.colors import print_success, input_colored
print_success("✓ All done!")
name = input_colored("Enter name: ", color="blue")
```

---

## 🔗 Data Flow

```
User Input (main.py CLI)
    ↓
Site Selection → ScraperFactory.create_scraper()
    ↓
Scraper.search_products()  [scrapers/]
    ↓
Raw Products (dict)
    ↓
DataCleaner.clean()  [pipeline/]
    ↓
Valid Products (list[Product])
    ↓
SQLiteStorage.save_products()  [storage/]
    ↓
Database: scraper.db
    ↓
User Options:
├─ Analyze: ProductAnalyzer  [analysis/]
├─ Export: DataExporter → CSV/Excel/JSON  [storage/]
└─ Stats: ProductAnalyzer.quick_stats()
```

---

## 💡 Design Principles

### 1. Separation of Concerns

Each module handles one responsibility:

| Module | Responsibility |
|--------|-----------------|
| scrapers/ | GET data |
| pipeline/ | VALIDATE data |
| storage/ | SAVE & SERVE data |
| analysis/ | ANALYZE data |
| models/ | STRUCTURE data |
| utils/ | SUPPORT all above |

### 2. Dependency Injection

Dependencies are passed, not constructed:

```python
# ❌ Bad
def search_products(self, query):
    http = HttpClient()  # Creates own dependency

# ✅ Good
def __init__(self, http_client: HttpClient):
    self.http = http_client  # Injected
```

### 3. Type Hints Everywhere

All functions have type hints for clarity and IDE support:

```python
def search_products(self, query: str, pages: int = 5) -> SearchResult:
    """Type hints help IDE autocomplete and catch bugs."""
    pass
```

### 4. No "God Objects"

No class does everything — split responsibilities:

```python
# ❌ Bad - Product class does everything
class Product:
    def scrape(self): ...
    def validate(self): ...
    def export_csv(self): ...
    def analyze(self): ...

# ✅ Good - Each class has one job
class Product: pass
class ProductScraper: ...
class DataCleaner: ...
class DataExporter: ...
class ProductAnalyzer: ...
```

---

## 🚀 Adding New Features

### Example: Add Product Watchlist

```python
# 1. Add model: src/models/watchlist.py
@dataclass
class Watchlist:
    product_ids: list[str]
    created_at: datetime

# 2. Add storage: src/storage/watchlist_storage.py
class WatchlistStorage:
    def save(self, watchlist: Watchlist) -> None: ...
    def load(self) -> Watchlist: ...

# 3. Add analysis: src/analysis/watchlist_analyzer.py
class WatchlistAnalyzer:
    def price_changes(self, watchlist: Watchlist) -> dict: ...

# 4. Integrate in main.py
from src.storage.watchlist_storage import WatchlistStorage
storage = WatchlistStorage()
watchlist = storage.load()
```

### Checklist
- [ ] Create in appropriate module  
- [ ] Add type hints  
- [ ] Add docstring  
- [ ] Add to module README.md  
- [ ] Test integration in main.py

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# Specific module
pytest tests/test_models.py

# With coverage
pytest --cov=src
```

### Test Structure

```
tests/
├── test_models.py             Product, Price, Rating models
├── test_scrapers.py           Scraper factory, base class
├── test_pipeline.py           Data cleaning
├── test_storage.py            Database, export
├── test_analysis.py           Analytics
└── test_utils.py              Helpers
```

---

## 📚 Documentation

Each module has detailed docs:

| Module | Quick Link |
|--------|-----------|
| scrapers | [scrapers/README.md](scrapers/README.md) |
| models | [models/README.md](models/README.md) |
| pipeline | [pipeline/README.md](pipeline/README.md) |
| storage | [storage/README.md](storage/README.md) |
| analysis | [analysis/README.md](analysis/README.md) |
| utils | [utils/README.md](utils/README.md) |

---

## 🔍 Code Style

This project follows strict standards:

- **Python 3.10+** — Type hints, dataclasses, walrus operator
- **Google-style docstrings** — See [BEST_PRACTICES.md](../../BEST_PRACTICES.md)
- **Black formatter** — Automatic formatting
- **Pylint** — Static analysis
- **Type hints** — 95%+ coverage

### Example

```python
"""Domain models for e-commerce products."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class Product:
    """Single product with normalized data.
    
    Attributes:
        product_id: Unique identifier (UUID)
        title: Product name
        price_current: Current selling price
        currency: ISO currency code
        source: Which site (amazon, noon, etc.)
        
    Example:
        >>> p = Product(
        ...     product_id=str(uuid.uuid4()),
        ...     title="Laptop",
        ...     price_current=999.99,
        ...     currency="USD",
        ...     source="amazon"
        ... )
        >>> print(p.title)
        "Laptop"
    """
    product_id: str
    title: str
    price_current: float
    currency: str = "USD"
    source: str = "generic"
    # ... more fields
```

---

## 📞 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found" | Run from project root: `python main.py` |
| Import error | Check `__init__.py` files exist in each folder |
| Type errors | Enable IDE type checking or run `mypy` |
| Test failures | Check `pytest` output, update fixtures |

---

## 🤝 Contributing

1. Add feature to appropriate module
2. Follow code style (Google docstrings, type hints)
3. Update module README.md
4. Add tests in tests/
5. Run `pytest` and ensure 100% pass
6. Submit PR

---

**Well-organized source code = Easy to extend, maintain, and debug!**

*See [../../BEST_PRACTICES.md](../../BEST_PRACTICES.md) for detailed coding standards.*
