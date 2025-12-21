"""
Base scraper module for web scraping with retry logic and rate limiting.

This module provides the foundation for all recipe scrapers with:
- HTTP client using httpx
- HTML parsing with BeautifulSoup
- Error handling and retry logic
- Rate limiting
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ScraperError(Exception):
    """Base exception for scraper errors."""

    pass


class RateLimitError(ScraperError):
    """Raised when rate limit is exceeded."""

    pass


class ParseError(ScraperError):
    """Raised when parsing fails."""

    pass


class RateLimiter:
    """Simple rate limiter for HTTP requests."""

    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Initialize rate limiter.

        Args:
          max_requests: Maximum number of requests allowed in time window
          time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: list[datetime] = []

    async def acquire(self) -> None:
        """
        Acquire permission to make a request.

        Raises:
          RateLimitError: If rate limit is exceeded
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)

        # Remove old requests
        self.requests = [req_time for req_time in self.requests if req_time > cutoff]

        if len(self.requests) >= self.max_requests:
            wait_time = (self.requests[0] - cutoff).total_seconds()
            logger.warning(f"Rate limit reached. Waiting {wait_time:.2f} seconds")
            await asyncio.sleep(wait_time)
            self.requests = self.requests[1:]

        self.requests.append(now)


class BaseScraper(ABC):
    """Base class for all recipe scrapers."""

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        rate_limiter: Optional[RateLimiter] = None,
    ):
        """
        Initialize base scraper.

        Args:
          timeout: Request timeout in seconds
          max_retries: Maximum number of retry attempts
          rate_limiter: Optional rate limiter instance
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limiter = rate_limiter or RateLimiter()
        self.client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Get or create HTTP client.

        Returns:
          httpx.AsyncClient instance
        """
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "User-Agent": "Personal-Recipe-Intelligence/1.0 (Recipe Collector Bot)",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
                },
                follow_redirects=True,
            )
        return self.client

    async def fetch_html(self, url: str) -> str:
        """
        Fetch HTML content from URL with retry logic.

        Args:
          url: URL to fetch

        Returns:
          HTML content as string

        Raises:
          ScraperError: If fetching fails after all retries
        """
        client = await self._get_client()
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                await self.rate_limiter.acquire()

                logger.info(
                    f"Fetching URL: {url} (attempt {attempt + 1}/{self.max_retries})"
                )
                response = await client.get(url)
                response.raise_for_status()

                return response.text

            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code in [429, 503]:
                    wait_time = 2**attempt
                    logger.warning(
                        f"HTTP {e.response.status_code} error. Retrying in {wait_time}s"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"HTTP error {e.response.status_code}: {url}")
                    raise ScraperError(f"HTTP error {e.response.status_code}") from e

            except httpx.RequestError as e:
                last_error = e
                wait_time = 2**attempt
                logger.warning(f"Request error: {e}. Retrying in {wait_time}s")
                await asyncio.sleep(wait_time)

        raise ScraperError(
            f"Failed to fetch URL after {self.max_retries} attempts"
        ) from last_error

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML string into BeautifulSoup object.

        Args:
          html: HTML content as string

        Returns:
          BeautifulSoup object
        """
        return BeautifulSoup(html, "html.parser")

    @abstractmethod
    async def scrape(self, url: str) -> Dict[str, Any]:
        """
        Scrape recipe from URL.

        Args:
          url: Recipe URL

        Returns:
          Dictionary containing recipe data

        Raises:
          ScraperError: If scraping fails
        """
        pass

    async def close(self) -> None:
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
