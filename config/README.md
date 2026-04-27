# ⚙️ Configuration

This directory contains all application settings and environment configuration management.

---

## 📋 Files

### `settings.py`

**Purpose:** Centralized configuration management with defaults and validation

**Import in your code:**
```python
from config.settings import Settings

settings = Settings()
print(settings.max_pages)           # Read a setting
print(settings.logs_dir)            # File paths
settings.validate()                 # Validate all ranges
```

---

## 🔧 All Configuration Options

### Scraping Behavior

| Setting | Env Variable | Default | Min | Max | Description |
|---------|--------------|---------|-----|-----|-------------|
| `max_pages` | `SCRAPER_MAX_PAGES` | `5` | 1 | 500 | Pages per scrape request |
| `delay_min` | `SCRAPER_DELAY_MIN` | `1.5` | 0.5 | 10 | Minimum delay (sec) |
| `delay_max` | `SCRAPER_DELAY_MAX` | `4.0` | 1 | 60 | Maximum delay (sec) |
| `timeout` | `SCRAPER_TIMEOUT` | `30` | 1 | 300 | Request timeout (sec) |
| `max_retries` | `SCRAPER_MAX_RETRIES` | `3` | 0 | 10 | Retry attempts |

### Logging

| Setting | Env Variable | Default | Values | Description |
|---------|--------------|---------|--------|-------------|
| `log_level` | `LOG_LEVEL` | `INFO` | DEBUG, INFO, WARNING, ERROR | Verbosity level |

### File Paths (Auto-set)

| Setting | Value | Purpose |
|---------|-------|---------|
| `project_root` | Parent of config/ | Base directory |
| `data_dir` | `data/` | Products, exports |
| `processed_dir` | `data/processed/` | Exported files |
| `logs_dir` | `logs/` | Application logs |
| `db_path` | `data/scraper.db` | SQLite database |

---

## 🎯 How Configuration Works

### Priority Order (Highest to Lowest)

1. **Environment variables** (set before running app)
2. **Defaults in settings.py** (fallback values)

### Example: Changing Max Pages

**Option 1: Environment Variable (Recommended)**

```bash
# Linux/macOS
export SCRAPER_MAX_PAGES=20
python main.py scrape amazon 20

# Windows (PowerShell)
$env:SCRAPER_MAX_PAGES = 20
python main.py scrape amazon 20

# Windows (CMD)
set SCRAPER_MAX_PAGES=20
python main.py scrape amazon 20
```

**Option 2: Edit settings.py**

```python
# config/settings.py
@dataclass
class Settings:
    max_pages: int = 20  # Change this default
```

**Option 3: In Python Code**

```python
from config.settings import Settings

settings = Settings()
settings.max_pages = 20  # Override for this session only
```

---

## 💡 Configuration Scenarios

### Scenario 1: Fast Scraping (Aggressive)

```bash
export SCRAPER_MAX_PAGES=50
export SCRAPER_DELAY_MIN=0.5
export SCRAPER_DELAY_MAX=1.5
export SCRAPER_TIMEOUT=15
python main.py scrape all 50
```

**Pros:** Fast data collection  
**Cons:** Higher chance of rate limiting / blocking

---

### Scenario 2: Safe Scraping (Ethical)

```bash
export SCRAPER_MAX_PAGES=5
export SCRAPER_DELAY_MIN=3.0
export SCRAPER_DELAY_MAX=7.0
export SCRAPER_TIMEOUT=60
python main.py scrape all 5
```

**Pros:** Respectful to target servers  
**Cons:** Slower collection  
**Best for:** Production use with real scrapers

---

### Scenario 3: Debugging

```bash
export LOG_LEVEL=DEBUG
export SCRAPER_TIMEOUT=30
export SCRAPER_MAX_RETRIES=5
python main.py scrape amazon 2
```

**Shows:** Full logging, stack traces, retry attempts  
**Check:** `logs/scraper_YYYY-MM-DD.log`

---

### Scenario 4: Testing

```bash
export SCRAPER_MAX_PAGES=1
export SCRAPER_DELAY_MIN=0.1
export SCRAPER_DELAY_MAX=0.5
python main.py scrape amazon 1 -q "test"
```

**Fastest:** Minimal delay, one page  
**Use for:** Quick validation

---

## 📊 Preset Configurations

**Copy and paste ready:**

### In PowerShell
```powershell
# Quick scrape
$env:SCRAPER_MAX_PAGES=5; python main.py scrape all 5

# Deep scrape
$env:SCRAPER_MAX_PAGES=50; $env:SCRAPER_DELAY_MIN=0.5; python main.py scrape all 50

# Safe scrape
$env:SCRAPER_MAX_PAGES=3; $env:SCRAPER_DELAY_MIN=5; python main.py scrape all 3

# Debug
$env:LOG_LEVEL="DEBUG"; python main.py scrape amazon 1
```

### In Bash
```bash
# Quick scrape
SCRAPER_MAX_PAGES=5 python main.py scrape all 5

# Deep scrape
SCRAPER_MAX_PAGES=50 SCRAPER_DELAY_MIN=0.5 python main.py scrape all 50

# Safe scrape
SCRAPER_MAX_PAGES=3 SCRAPER_DELAY_MIN=5 python main.py scrape all 3

# Debug
LOG_LEVEL=DEBUG python main.py scrape amazon 1
```

---

## ✅ Validation

Settings are automatically validated on app start:

```python
from config.settings import Settings

settings = Settings()
settings.validate()  # Raises ValueError if out of range
```

**Example error:**
```
ValueError: max_pages must be 1–500, got: 501
```

---

## 📝 Advanced Usage

### Custom Settings Class

Extend settings for your extensions:

```python
from config.settings import Settings

class CustomSettings(Settings):
    my_custom_option: str = "default"
    
    def validate(self):
        super().validate()
        if not self.my_custom_option:
            raise ValueError("my_custom_option cannot be empty")
```

---

## 🚨 Common Issues

| Problem | Solution |
|---------|----------|
| Settings not applying | Restart app after `export` / `set` command |
| "Invalid range" error | Check min/max in error message, adjust value |
| Environment variable ignored | Confirm: `echo $SCRAPER_MAX_PAGES` (Unix) or `echo %SCRAPER_MAX_PAGES%` (Windows) |
| Timeout too short | Increase: `export SCRAPER_TIMEOUT=60` |
| Rate limited | Increase delays: `SCRAPER_DELAY_MIN=5 SCRAPER_DELAY_MAX=10` |

---

## 📚 File Paths Reference

Access paths in code:

```python
from config.settings import Settings

s = Settings()

# Directories
s.project_root      # Repo root
s.data_dir          # Product data directory
s.processed_dir     # Export directory
s.logs_dir          # Log files directory

# Database
s.db_path           # "data/scraper.db"
```

---

## 🔐 Best Practices

1. **Use environment variables in production** — easier to update without editing code
2. **Don't commit changes to settings.py** — use `.env` or shell exports
3. **Validate settings** — call `settings.validate()` in initialization
4. **Document custom additions** — if you extend Settings, update this file
5. **Back up settings** — save working configs in comments or env files

---

## 📞 Need Help?

- Check root [README.md](../README.md) for quick start
- See [data/README.md](../data/README.md) for data-specific settings
- Enable debug: `export LOG_LEVEL=DEBUG && python main.py`
- Check logs: `tail -50 logs/scraper_*.log`

---

**Last Updated:** 2026-03-29  
**Maintained by:** Mohamed Darwish
