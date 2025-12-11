"""
Site-specific scrapers package.

This package contains scrapers for specific recipe websites:
- Cookpad
- Delish Kitchen
- Generic (fallback using schema.org or common patterns)
"""

from typing import Dict, Type
from urllib.parse import urlparse

from backend.scraper.base import BaseScraper
from backend.scraper.sites.cookpad import CookpadScraper
from backend.scraper.sites.delish_kitchen import DelishKitchenScraper
from backend.scraper.sites.generic import GenericScraper

# Map of domain patterns to scraper classes
SCRAPER_MAP: Dict[str, Type[BaseScraper]] = {
  "cookpad.com": CookpadScraper,
  "delishkitchen.tv": DelishKitchenScraper,
}


def get_scraper_for_url(url: str) -> BaseScraper:
  """
  Get appropriate scraper for given URL.

  Args:
    url: Recipe URL

  Returns:
    Scraper instance for the URL
  """
  parsed = urlparse(url)
  domain = parsed.netloc.lower()

  # Remove www. prefix
  if domain.startswith("www."):
    domain = domain[4:]

  # Find matching scraper
  for pattern, scraper_class in SCRAPER_MAP.items():
    if pattern in domain:
      return scraper_class()

  # Fallback to generic scraper
  return GenericScraper()


__all__ = [
  "CookpadScraper",
  "DelishKitchenScraper",
  "GenericScraper",
  "get_scraper_for_url",
  "SCRAPER_MAP",
]
