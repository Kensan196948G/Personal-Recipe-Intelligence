"""
Scraper Module - Web recipe scraping functionality

Provides scrapers for various recipe websites:
- CookpadScraper: For cookpad.com
- DelishKitchenScraper: For delishkitchen.tv
- GenericScraper: Fallback for any site using schema.org or common patterns
"""

from backend.scraper.sites import (
  CookpadScraper,
  DelishKitchenScraper,
  GenericScraper,
  get_scraper_for_url,
)

__all__ = [
  "CookpadScraper",
  "DelishKitchenScraper",
  "GenericScraper",
  "get_scraper_for_url",
]
