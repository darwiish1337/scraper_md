"""
src/utils/helpers.py

Stateless utility functions shared across scrapers and pipeline.

Author : M-D (Mohamed Darwish)
"""

import re
import urllib.parse
from decimal import Decimal, InvalidOperation
from typing import Optional

from src.utils.logger import get_logger


logger = get_logger(__name__)


def clean_text(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    cleaned = re.sub(r"\s+", " ", text.strip())
    return cleaned if cleaned else None


def truncate(text: Optional[str], max_length: int = 500) -> Optional[str]:
    if not text:
        return None
    return text[:max_length - 3] + "..." if len(text) > max_length else text


_CURRENCY_PAT = re.compile(
    r"[€$£¥₹₪﷼AEDSARUSDEGPNGNKESGHSTNDsar\s,]", re.IGNORECASE
)


def parse_price(raw: Optional[str]) -> Optional[Decimal]:
    if not raw:
        return None
    text = raw.strip()
    if re.search(r"free|n/a|unavailable", text, re.IGNORECASE):
        return None

    cleaned = _CURRENCY_PAT.sub("", text).strip()

    # European format: 1.299,99
    if re.match(r"^\d{1,3}(\.\d{3})*(,\d+)?$", cleaned) and "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")

    # Standard: 1,299.99
    elif re.match(r"^\d{1,3}(,\d{3})*(\.\d+)?$", cleaned):
        cleaned = cleaned.replace(",", "")

    match = re.search(r"\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    try:
        return Decimal(match.group())
    except InvalidOperation:
        return None


def detect_currency(raw: Optional[str]) -> str:
    if not raw:
        return "USD"
    t = raw.upper()
    mapping = {
        "EGP": ["EGP", "ج.م"],
        "SAR": ["SAR", "ر.س", "﷼"],
        "AED": ["AED", "د.إ"],
        "NGN": ["NGN", "₦"],
        "GBP": ["GBP", "£"],
        "EUR": ["EUR", "€"],
        "USD": ["USD", "$"],
        "INR": ["INR", "₹"],
        "MAD": ["MAD", "DH"],
    }
    for code, syms in mapping.items():
        if any(s in t for s in syms):
            return code
    return "USD"


def parse_rating(raw: Optional[str]) -> Optional[float]:
    if not raw:
        return None
    match = re.search(r"(\d+[.,]\d+|\d+)", raw.replace(",", "."))
    if not match:
        return None
    try:
        v = float(match.group().replace(",", "."))
        if v > 5:
            v = v / 2
        return round(min(v, 5.0), 1)
    except ValueError:
        return None


def parse_review_count(raw: Optional[str]) -> int:
    if not raw:
        return 0
    k = re.search(r"([\d.]+)\s*[kK]", raw)
    m = re.search(r"([\d.]+)\s*[mM]", raw)
    if k:
        try:
            return int(float(k.group(1)) * 1_000)
        except ValueError:
            pass
    if m:
        try:
            return int(float(m.group(1)) * 1_000_000)
        except ValueError:
            pass
    nums = re.findall(r"\d+", raw.replace(",", ""))
    return int(nums[0]) if nums else 0


def normalise_url(url: str, base_url: str) -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return urllib.parse.urljoin(base_url, url)
