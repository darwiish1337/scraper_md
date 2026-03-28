#!/usr/bin/env python3
"""
main.py — M-D Web Scraper

Interactive and argument-driven CLI for e-commerce data collection.
Supports Amazon, Noon, AliExpress, Jumia, eBay, and Books to Scrape.

Author  : M-D (Mohamed Darwish)
Usage   :
    python main.py                          # interactive mode
    python main.py scrape amazon 5          # scrape amazon, 5 pages
    python main.py scrape all 3             # scrape all sites
    python main.py analyze                  # analyze stored data
    python main.py export csv               # export to CSV
    python main.py stats                    # quick stats
    python main.py --help
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from src.scrapers.factory import create_scraper, list_sites, site_keys, REGISTRY
from src.scrapers.base import ScraperConfig
from src.scrapers.simulated import SimulatedScraper, NOUNS
from src.pipeline.cleaner import clean_products
from src.storage.sqlite_storage import SQLiteStorage
from src.storage.exporter import DataExporter
from src.analysis.analyzer import ProductAnalyzer
from src.utils.http_client import HttpClient
from src.utils.logger import configure_logging, get_logger
from src.utils.colors import (
    C, style, print_header, print_section, ok, info, warn, error, dim,
    label_value, print_table, ProgressBar,
    prompt_choice, prompt_multi_choice, prompt_text, prompt_int, confirm,
)


configure_logging(level=settings.log_level, log_dir=str(settings.logs_dir))
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------

def run_scrape(
    sources:    list[str],
    max_pages:  int,
    category:   str | None,
    query:      str | None,
    fmt:        str,
    output_stem: str | None = None,
) -> None:
    """Scrape one or more sites and export results."""

    db       = SQLiteStorage(settings.db_path)
    exporter = DataExporter(str(settings.processed_dir))
    all_prods = []

    cfg = ScraperConfig(
        max_pages   = max_pages,
        delay_min   = settings.delay_min,
        delay_max   = settings.delay_max,
        timeout     = settings.timeout,
        max_retries = settings.max_retries,
    )

    for key in sources:
        site = REGISTRY[key]
        print()
        info(
            f"Scraping {style(site.name, C.BOLD, C.BWHITE)}"
            f"  {style('·', C.DIM)}  "
            f"{style(site.mode, C.BYELLOW if site.mode == 'simulated' else C.BGREEN)}"
            f"  {style('·', C.DIM)}  "
            f"{style(site.currency, C.CYAN)}"
        )

        bar     = ProgressBar(total=max_pages, label=f"{site.name} pages")
        scraper = create_scraper(key, cfg)

        if isinstance(scraper, SimulatedScraper) and category:
            valid_cats = scraper.available_categories()
            if not any(category.lower() in c.lower() for c in valid_cats):
                warn(f"Category '{category}' not found for {site.name}. Using all categories.")
                category = None

        result = scraper.search_products(
            query     = query or "",
            max_pages = max_pages,
            category  = category,
        )

        bar.update(max_pages, f"{result.total_products} products")

        if not result.success:
            error(f"Scrape failed for {site.name}.")
            if result.errors:
                for e in result.errors[:3]:
                    dim(f"  {e}")
            continue

        cleaned = clean_products(result.products)
        saved   = db.save_products(cleaned)
        db.log_run(result)

        ok(f"{saved} products saved — {result.duration_seconds:.1f}s")
        all_prods.extend(cleaned)

    if not all_prods:
        warn("No products collected.")
        return

    # Export
    print()
    info(f"Exporting {len(all_prods)} products...")
    stem = output_stem or "_".join(sources)

    if fmt == "csv":
        from datetime import datetime
        ts   = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = exporter.to_csv(all_prods, f"{stem}_{ts}.csv")
        ok(f"CSV  →  {path}")
    elif fmt == "excel":
        from datetime import datetime
        ts   = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = exporter.to_excel(all_prods, f"{stem}_{ts}.xlsx")
        ok(f"Excel →  {path}")
    elif fmt == "json":
        from datetime import datetime
        ts   = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = exporter.to_json(all_prods, f"{stem}_{ts}.json")
        ok(f"JSON →  {path}")
    else:
        paths = exporter.export_all(all_prods, stem)
        for f_fmt, f_path in paths.items():
            ok(f"{f_fmt.upper():<6} →  {f_path}")

    print()
    print_summary_box(all_prods)


def run_analyze() -> None:
    """Print analysis of all stored products."""
    db   = SQLiteStorage(settings.db_path)
    rows = db.get_all_dicts()

    if not rows:
        warn("No data in database. Run a scrape first.")
        return

    # Reconstruct Product objects for the analyzer
    from src.models.product import Product, ProductPrice, ProductRating, ScraperSource, Availability
    from decimal import Decimal

    products = []
    for r in rows:
        try:
            p = Product(
                title        = r["title"],
                url          = r["url"],
                source       = ScraperSource(r["source"]),
                price        = ProductPrice(
                    current  = Decimal(str(r["price_current"])),
                    original = Decimal(str(r["price_original"])) if r.get("price_original") else None,
                    currency = r.get("currency", "USD"),
                ),
                availability = Availability(r.get("availability", "unknown")),
                brand        = r.get("brand"),
                category     = r.get("category"),
                rating       = ProductRating(
                    score         = r["rating_score"],
                    reviews_count = r.get("reviews_count", 0),
                ) if r.get("rating_score") else None,
            )
            products.append(p)
        except Exception:
            pass

    if not products:
        warn("Could not reconstruct products for analysis.")
        return

    analyzer = ProductAnalyzer(products)

    print_section("Price Statistics")
    stats = analyzer.price_statistics()
    label_value("Count",     f"{stats['count']:,}")
    label_value("Mean",      f"{stats['mean']:.2f}")
    label_value("Median",    f"{stats['median']:.2f}")
    label_value("Std dev",   f"{stats['std_dev']:.2f}")
    label_value("Min",       f"{stats['min']:.2f}")
    label_value("Max",       f"{stats['max']:.2f}")
    label_value("P25",       f"{stats['p25']:.2f}")
    label_value("P75",       f"{stats['p75']:.2f}")

    print_section("By Source")
    by_src = analyzer.by_source()
    print_table(
        ["Source", "Count", "Avg Price", "Currency", "Avg Rating"],
        [
            [
                r["source"],
                str(r["count"]),
                f"{r['avg_price']:.2f}" if r.get("avg_price") else "N/A",
                r.get("currency", "?"),
                f"{r['avg_rating']:.1f}" if r.get("avg_rating") else "N/A",
            ]
            for r in by_src
        ],
        col_widths=[16, 8, 12, 10, 12],
    )

    print_section("Top Categories")
    by_cat = analyzer.by_category()[:15]
    print_table(
        ["Category", "Count", "Avg Price", "Avg Rating", "Discounted %"],
        [
            [
                r["category"],
                str(r["count"]),
                f"{r['avg_price']:.2f}" if r.get("avg_price") else "N/A",
                f"{r['avg_rating']:.1f}" if r.get("avg_rating") else "N/A",
                f"{r['discount_pct']:.1f}%",
            ]
            for r in by_cat
        ],
        col_widths=[22, 7, 11, 12, 14],
    )

    print_section("Top 5 Rated")
    for p in analyzer.top_rated(5):
        score = f"{p.rating.score:.1f}" if p.rating else "?"
        print(
            f"  {style(score, C.BGREEN, C.BOLD):>5}  "
            f"{style(p.title[:50], C.WHITE):<52}  "
            f"{style(p.category or 'N/A', C.DIM)}"
        )

    print_section("Best Discounts")
    for p in analyzer.best_discounts(5):
        disc = f"{p.price.discount_percentage:.1f}%" if p.price.discount_percentage else "?"
        print(
            f"  {style(disc, C.BYELLOW, C.BOLD):>7}  "
            f"{style(p.title[:50], C.WHITE):<52}  "
            f"{style(str(p.price), C.DIM)}"
        )

    avail = analyzer.availability_summary()
    print_section("Availability")
    for k, v in avail.items():
        color = C.BGREEN if k == "in_stock" else (C.BYELLOW if k == "limited" else C.BRED)
        print(
            f"  {style(k:<15), C.DIM}  "
            f"{style(str(v['count']), color)}  "
            f"{style(f\"({v['pct']}%)\", C.DIM)}"
        )

    print()


def run_stats() -> None:
    """Print quick database stats."""
    db    = SQLiteStorage(settings.db_path)
    stats = db.get_stats()
    total = db.total_count()

    print_section("Database Stats")
    label_value("Location",   settings.db_path)
    label_value("Products",   f"{total:,}")
    label_value("Sources",    str(stats.get("sources", 0)))
    label_value("Categories", str(stats.get("categories", 0)))
    avg = stats.get("avg_price")
    if avg:
        label_value("Avg price",  f"{avg:.2f}")
    label_value("Discounted", str(stats.get("discounted", 0)))
    avg_r = stats.get("avg_rating")
    if avg_r:
        label_value("Avg rating", f"{avg_r:.2f}")
    label_value("Last scraped", str(stats.get("last_scraped", "never")))
    print()


def run_export(fmt: str) -> None:
    """Export existing database to files."""
    db   = SQLiteStorage(settings.db_path)
    rows = db.get_all_dicts()

    if not rows:
        warn("Nothing in the database to export.")
        return

    from src.models.product import Product, ProductPrice, ScraperSource, Availability
    from decimal import Decimal

    products = []
    for r in rows:
        try:
            products.append(Product(
                title        = r["title"],
                url          = r["url"],
                source       = ScraperSource(r["source"]),
                price        = ProductPrice(
                    current  = Decimal(str(r["price_current"])),
                    currency = r.get("currency", "USD"),
                ),
                availability = Availability(r.get("availability", "unknown")),
                brand        = r.get("brand"),
                category     = r.get("category"),
                description  = r.get("description"),
            ))
        except Exception:
            pass

    exporter = DataExporter(str(settings.processed_dir))
    info(f"Exporting {len(products)} products as {fmt.upper()}...")

    if fmt == "csv":
        path = exporter.to_csv(products, "export.csv")
    elif fmt == "excel":
        path = exporter.to_excel(products, "export.xlsx")
    elif fmt == "json":
        path = exporter.to_json(products, "export.json")
    else:
        paths = exporter.export_all(products, "export")
        for f, p in paths.items():
            ok(f"{f.upper():<6} →  {p}")
        return

    ok(f"Exported  →  {path}")
    print()


# ---------------------------------------------------------------------------
# Interactive mode
# ---------------------------------------------------------------------------

def interactive_mode() -> None:
    """Full interactive guided session."""

    while True:
        print_section("Main Menu")
        choice = prompt_choice(
            "What do you want to do?",
            [
                "Scrape products from a site",
                "Analyze stored data",
                "Export data to file",
                "View database stats",
                "Exit",
            ],
        )

        if choice == 0:
            _interactive_scrape()
        elif choice == 1:
            run_analyze()
        elif choice == 2:
            _interactive_export()
        elif choice == 3:
            run_stats()
        elif choice == 4:
            print()
            dim("Goodbye.")
            print()
            sys.exit(0)


def _interactive_scrape() -> None:
    """Interactive scrape configuration wizard."""

    # --- Site selection ---
    print_section("Site Selection")

    sites   = list_sites()
    labels  = []
    for key, info_ in sites:
        mode_str = style("[live]",      C.BGREEN)  if info_.mode == "live" else style("[simulated]", C.BYELLOW)
        labels.append(f"{info_.name:<18} {mode_str}  {style(info_.currency, C.CYAN)}  —  {info_.description}")
    labels.append("All sites")

    indices = prompt_multi_choice("Select sites to scrape:", labels)

    if len(labels) - 1 in indices:
        selected_keys = [k for k, _ in sites]
    else:
        selected_keys = [sites[i][0] for i in indices if i < len(sites)]

    # --- Category selection ---
    print_section("Category")
    use_cat = confirm("Filter by a specific category?", default=False)
    category = None

    if use_cat:
        # Show categories from the first selected site
        first_key = selected_keys[0]
        first_scraper = create_scraper(first_key)
        if isinstance(first_scraper, SimulatedScraper):
            all_cats = first_scraper.available_categories()
            cat_labels  = all_cats + ["All categories (no filter)"]
            cat_idx     = prompt_choice("Select category:", cat_labels, default=len(cat_labels) - 1)
            if cat_idx < len(all_cats):
                category = all_cats[cat_idx]
        else:
            # Live scraper — fetch real categories
            info("Fetching categories from site...")
            from src.scrapers.books_scraper import BooksScraper
            if isinstance(first_scraper, BooksScraper):
                real_cats = list(first_scraper.get_categories().keys())
                if real_cats:
                    real_cats.append("All categories")
                    cat_idx  = prompt_choice("Select category:", real_cats, default=len(real_cats) - 1)
                    if cat_idx < len(real_cats) - 1:
                        category = real_cats[cat_idx]

    # --- Query ---
    print_section("Search Query")
    use_query = confirm("Add a search keyword?", default=False)
    query = None
    if use_query:
        query = prompt_text("Enter keyword", allow_empty=True) or None

    # --- Page count ---
    print_section("Volume")
    max_pages = prompt_int(
        "Pages per site (20 products/page)",
        default = 5,
        min_val = 1,
        max_val = 200,
    )
    info(f"Estimated products: ~{max_pages * 20 * len(selected_keys):,}")

    # --- Output format ---
    print_section("Export Format")
    fmt_idx = prompt_choice(
        "Output format:",
        ["CSV (recommended for Kaggle)", "Excel (.xlsx)", "JSON", "All three"],
        default = 0,
    )
    fmt_map = {0: "csv", 1: "excel", 2: "json", 3: "all"}
    fmt     = fmt_map[fmt_idx]

    # --- Confirm ---
    print_section("Summary")
    label_value("Sites",    ", ".join(selected_keys))
    label_value("Category", category or "All")
    label_value("Query",    query or "None")
    label_value("Pages",    str(max_pages))
    label_value("Format",   fmt.upper())

    if not confirm("Start scraping?", default=True):
        warn("Cancelled.")
        return

    run_scrape(
        sources   = selected_keys,
        max_pages = max_pages,
        category  = category,
        query     = query,
        fmt       = fmt,
    )


def _interactive_export() -> None:
    fmt_idx = prompt_choice(
        "Export format:",
        ["CSV", "Excel (.xlsx)", "JSON", "All three"],
        default = 0,
    )
    fmt_map = {0: "csv", 1: "excel", 2: "json", 3: "all"}
    run_export(fmt_map[fmt_idx])


# ---------------------------------------------------------------------------
# Print helpers
# ---------------------------------------------------------------------------

def print_summary_box(products) -> None:
    """Print a compact summary after a scrape run."""
    if not products:
        return

    prices = [float(p.price.current) for p in products if p.price.current > 0]
    disc   = sum(1 for p in products if p.price.has_discount)
    cats   = len(set(p.category for p in products if p.category))
    src    = len(set(p.source.value for p in products))

    import statistics as st
    w  = 50
    hr = style("  " + "─" * w, C.DIM)

    print(hr)
    print(style(f"  {'Scrape complete':^{w}}", C.BOLD, C.BWHITE))
    print(hr)
    label_value("Products",    f"{len(products):,}")
    label_value("Sources",     str(src))
    label_value("Categories",  str(cats))
    if prices:
        label_value("Avg price",   f"{st.mean(prices):.2f}")
        label_value("Min / Max",   f"{min(prices):.2f}  /  {max(prices):.2f}")
    label_value("Discounted",  f"{disc} ({disc/len(products)*100:.1f}%)")
    print(hr)
    print()


# ---------------------------------------------------------------------------
# Argument-mode CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog        = "md-scraper",
        description = "M-D Web Scraper — E-Commerce Data Collection",
        epilog      = """
examples:
  python main.py                          interactive mode
  python main.py scrape amazon 10         amazon, 10 pages
  python main.py scrape noon 5 -c Fashion
  python main.py scrape all 3             all sites, 3 pages each
  python main.py analyze
  python main.py export csv
  python main.py stats
""",
        formatter_class = argparse.RawDescriptionHelpFormatter,
    )

    sub = p.add_subparsers(dest="cmd")

    # scrape
    sc = sub.add_parser("scrape", help="Run the scraper")
    sc.add_argument("source",   choices=site_keys() + ["all"], help="Site or 'all'")
    sc.add_argument("pages",    type=int, nargs="?", default=5, help="Pages per site (default 5)")
    sc.add_argument("-c", "--category", default=None, help="Category filter")
    sc.add_argument("-q", "--query",    default=None, help="Search keyword")
    sc.add_argument("-f", "--format",   choices=["csv", "excel", "json", "all"], default="all")
    sc.add_argument("-o", "--output",   default=None, help="Output filename stem")

    # analyze
    sub.add_parser("analyze", help="Analyze stored products")

    # export
    ex = sub.add_parser("export", help="Export database to file")
    ex.add_argument("format", choices=["csv", "excel", "json", "all"], nargs="?", default="all")

    # stats
    sub.add_parser("stats", help="Quick database stats")

    # sites
    sub.add_parser("sites", help="List all available sites")

    return p


def cmd_sites() -> None:
    print_section("Available Sites")
    for key, site in list_sites():
        mode_color = C.BGREEN if site.mode == "live" else C.BYELLOW
        print(
            f"  {style(key:<12), C.BOLD}  "
            f"{style(site.name:<18)}  "
            f"{style(site.mode, mode_color):<12}  "
            f"{style(site.currency, C.CYAN):<6}  "
            f"{style(site.description, C.DIM)}"
        )
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print_header()

    parser = build_parser()
    args   = parser.parse_args()

    if args.cmd is None:
        interactive_mode()
        return

    t0 = time.time()

    if args.cmd == "scrape":
        sources = site_keys() if args.source == "all" else [args.source]
        run_scrape(
            sources      = sources,
            max_pages    = args.pages,
            category     = args.category,
            query        = args.query,
            fmt          = args.format,
            output_stem  = args.output,
        )

    elif args.cmd == "analyze":
        run_analyze()

    elif args.cmd == "export":
        run_export(args.format)

    elif args.cmd == "stats":
        run_stats()

    elif args.cmd == "sites":
        cmd_sites()

    elapsed = time.time() - t0
    dim(f"  Done in {elapsed:.1f}s")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        warn("Interrupted.")
        print()
        sys.exit(0)
