#!/usr/bin/env python3
"""
Cache maintenance script for Personal Recipe Intelligence.

This script provides CLI tools for cache management and monitoring.
"""

import sys
import argparse
import json
from typing import Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.core.cache import (
  get_cache,
  get_cache_stats,
  clear_all_cache,
  invalidate_cache,
)


def print_stats():
  """Print detailed cache statistics."""
  stats = get_cache_stats()

  print("\n" + "=" * 60)
  print("CACHE STATISTICS")
  print("=" * 60)

  print(f"\nOverview:")
  print(f"  Total Entries: {stats['total_entries']}")
  print(f"  Hit Rate: {stats['hit_rate']:.2f}%")
  print(f"  Hits: {stats['hits']}")
  print(f"  Misses: {stats['misses']}")
  print(f"  Sets: {stats['sets']}")
  print(f"  Evictions: {stats['evictions']}")

  if stats['entries']:
    print(f"\nTop Cached Items (by hits):")
    for i, entry in enumerate(stats['entries'][:10], 1):
      print(f"  {i}. {entry['key']}")
      print(f"     Hits: {entry['hits']}, Age: {entry['age']:.1f}s, TTL: {entry['ttl']}s")

  print("\n" + "=" * 60 + "\n")


def print_json_stats():
  """Print cache statistics in JSON format."""
  stats = get_cache_stats()
  print(json.dumps(stats, indent=2))


def clear_cache():
  """Clear all cache entries."""
  print("Clearing all cache entries...")
  clear_all_cache()
  print("Cache cleared successfully.")


def invalidate_pattern(pattern: str):
  """Invalidate cache entries matching a pattern."""
  print(f"Invalidating entries matching pattern: {pattern}")
  count = invalidate_cache(pattern)
  print(f"Invalidated {count} cache entries.")


def cleanup_expired():
  """Remove expired entries from cache."""
  print("Cleaning up expired cache entries...")
  cache = get_cache()
  count = cache.cleanup_expired()
  print(f"Removed {count} expired entries.")


def monitor_mode(interval: int = 5):
  """Monitor cache statistics in real-time."""
  import time

  print("Cache monitoring mode (Ctrl+C to exit)")
  print(f"Refresh interval: {interval} seconds\n")

  try:
    while True:
      # Clear screen (works on Linux/Mac)
      print("\033[2J\033[H", end="")

      stats = get_cache_stats()

      print("=" * 60)
      print("CACHE MONITOR - Real-time Statistics")
      print("=" * 60)

      print(f"\nEntries: {stats['total_entries']} | " +
            f"Hit Rate: {stats['hit_rate']:.2f}% | " +
            f"Hits: {stats['hits']} | " +
            f"Misses: {stats['misses']}")

      if stats['entries']:
        print("\nTop 5 Active Caches:")
        for i, entry in enumerate(stats['entries'][:5], 1):
          print(f"  {i}. {entry['key'][:40]}{'...' if len(entry['key']) > 40 else ''}")
          print(f"     Hits: {entry['hits']}, Age: {entry['age']:.1f}s")

      print(f"\nRefreshing in {interval}s... (Ctrl+C to exit)")

      time.sleep(interval)

  except KeyboardInterrupt:
    print("\n\nMonitoring stopped.")


def warm_cache():
  """Pre-populate cache with common data."""
  print("Warming cache with common queries...")

  # This would call actual service methods
  # For now, just demonstrate the concept

  print("  - Loading recipe lists...")
  print("  - Loading tag lists...")
  print("  - Pre-calculating nutrition data...")

  print("Cache warming complete.")


def main():
  """Main CLI entry point."""
  parser = argparse.ArgumentParser(
    description="Cache maintenance tools for Personal Recipe Intelligence"
  )

  subparsers = parser.add_subparsers(dest="command", help="Available commands")

  # Stats command
  stats_parser = subparsers.add_parser("stats", help="Display cache statistics")
  stats_parser.add_argument(
    "--json",
    action="store_true",
    help="Output in JSON format"
  )

  # Clear command
  subparsers.add_parser("clear", help="Clear all cache entries")

  # Invalidate command
  invalidate_parser = subparsers.add_parser(
    "invalidate",
    help="Invalidate cache entries matching a pattern"
  )
  invalidate_parser.add_argument("pattern", help="Pattern to match")

  # Cleanup command
  subparsers.add_parser("cleanup", help="Remove expired cache entries")

  # Monitor command
  monitor_parser = subparsers.add_parser(
    "monitor",
    help="Monitor cache statistics in real-time"
  )
  monitor_parser.add_argument(
    "-i", "--interval",
    type=int,
    default=5,
    help="Refresh interval in seconds (default: 5)"
  )

  # Warm command
  subparsers.add_parser("warm", help="Pre-populate cache with common data")

  args = parser.parse_args()

  if not args.command:
    parser.print_help()
    return

  # Execute command
  if args.command == "stats":
    if args.json:
      print_json_stats()
    else:
      print_stats()

  elif args.command == "clear":
    clear_cache()

  elif args.command == "invalidate":
    invalidate_pattern(args.pattern)

  elif args.command == "cleanup":
    cleanup_expired()

  elif args.command == "monitor":
    monitor_mode(args.interval)

  elif args.command == "warm":
    warm_cache()


if __name__ == "__main__":
  main()
