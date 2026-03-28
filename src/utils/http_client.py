"""
src/utils/http_client.py

Robust HTTP client with retry, rate limiting, and user-agent rotation.
Injected into all scrapers via Dependency Inversion.

Author : M-D (Mohamed Darwish)
"""

import random
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.utils.logger import get_logger


logger = get_logger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

DEFAULT_HEADERS = {
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
    "DNT":             "1",
}


class HttpClient:
    """
    Shared HTTP client for all scrapers.
    Never construct requests.Session directly in a scraper.
    """

    def __init__(
        self,
        delay_min:   float = 1.5,
        delay_max:   float = 4.0,
        timeout:     int   = 30,
        max_retries: int   = 3,
        proxies:     Optional[dict] = None,
    ):
        self.delay_min        = delay_min
        self.delay_max        = delay_max
        self.timeout          = timeout
        self._last_req: float = 0.0
        self._session         = self._build_session(max_retries, proxies or {})

    def _build_session(self, max_retries: int, proxies: dict) -> requests.Session:
        session = requests.Session()
        retry   = Retry(
            total            = max_retries,
            backoff_factor   = 1,
            status_forcelist = {429, 500, 502, 503, 504},
            allowed_methods  = {"GET"},
            raise_on_status  = False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://",  adapter)
        session.headers.update(DEFAULT_HEADERS)
        if proxies:
            session.proxies.update(proxies)
        return session

    def _throttle(self) -> None:
        elapsed = time.time() - self._last_req
        wait    = random.uniform(self.delay_min, self.delay_max)
        if elapsed < wait:
            time.sleep(wait - elapsed)

    def get(
        self,
        url:     str,
        params:  Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> Optional[requests.Response]:
        self._throttle()
        self._session.headers["User-Agent"] = random.choice(USER_AGENTS)

        try:
            resp = self._session.get(
                url, params=params, headers=headers or {}, timeout=self.timeout
            )
            self._last_req = time.time()

            if resp.status_code == 200:
                return resp
            logger.warning(f"HTTP {resp.status_code}: {url}")
            return None

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection failed: {url} — {e}")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"Timeout ({self.timeout}s): {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {url} — {e}")
            return None

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *_) -> None:
        self.close()
