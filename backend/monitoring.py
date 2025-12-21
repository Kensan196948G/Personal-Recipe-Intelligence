"""
System monitoring utilities for Personal Recipe Intelligence
Memory and performance monitoring per CLAUDE.md requirements
"""

import psutil
import os
import logging
import time
from typing import Dict, Any, Optional
from contextlib import contextmanager
from functools import wraps

logger = logging.getLogger(__name__)


class MemoryMonitor:
    """Monitor and log memory usage"""

    @staticmethod
    def get_memory_info() -> Dict[str, float]:
        """
        Get current process memory information.

        Returns:
            Dict with RSS (actual memory) and VMS (virtual memory) in MB
        """
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()

        return {
            "rss_mb": mem_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": mem_info.vms / 1024 / 1024,  # Virtual Memory Size
            "percent": process.memory_percent(),
        }

    @staticmethod
    def log_memory_usage(context: str = "") -> None:
        """
        Log current memory usage.

        Args:
            context: Description of when this measurement was taken
        """
        mem = MemoryMonitor.get_memory_info()

        logger.info(
            f"Memory usage {context}: RSS={mem['rss_mb']:.2f}MB, "
            f"VMS={mem['vms_mb']:.2f}MB, "
            f"Percent={mem['percent']:.2f}%",
            extra={
                "memory_rss_mb": mem["rss_mb"],
                "memory_vms_mb": mem["vms_mb"],
                "memory_percent": mem["percent"],
                "context": context,
            },
        )

    @staticmethod
    @contextmanager
    def track_memory(operation_name: str):
        """
        Context manager to track memory usage during an operation.

        Args:
            operation_name: Name of the operation being tracked

        Example:
            with MemoryMonitor.track_memory("OCR processing"):
                result = process_image(image_path)
        """
        mem_before = MemoryMonitor.get_memory_info()
        start_time = time.time()

        logger.debug(
            f"Memory before {operation_name}: {mem_before['rss_mb']:.2f}MB"
        )

        try:
            yield
        finally:
            mem_after = MemoryMonitor.get_memory_info()
            duration = time.time() - start_time
            delta_mb = mem_after["rss_mb"] - mem_before["rss_mb"]

            logger.info(
                f"Memory after {operation_name}: {mem_after['rss_mb']:.2f}MB "
                f"(delta: {delta_mb:+.2f}MB, duration: {duration:.2f}s)",
                extra={
                    "operation": operation_name,
                    "memory_before_mb": mem_before["rss_mb"],
                    "memory_after_mb": mem_after["rss_mb"],
                    "memory_delta_mb": delta_mb,
                    "duration_seconds": duration,
                },
            )


class PerformanceMonitor:
    """Monitor performance metrics"""

    @staticmethod
    @contextmanager
    def track_time(operation_name: str, threshold_ms: float = 200.0):
        """
        Context manager to track execution time.

        Args:
            operation_name: Name of the operation
            threshold_ms: Log warning if exceeds this threshold (default: 200ms per CLAUDE.md)

        Example:
            with PerformanceMonitor.track_time("Database query", threshold_ms=100):
                results = execute_query()
        """
        start_time = time.time()

        try:
            yield
        finally:
            duration = time.time() - start_time
            duration_ms = duration * 1000

            log_data = {
                "operation": operation_name,
                "duration_ms": round(duration_ms, 2),
            }

            if duration_ms > threshold_ms:
                logger.warning(
                    f"SLOW OPERATION: {operation_name} took {duration_ms:.2f}ms "
                    f"(threshold: {threshold_ms}ms)",
                    extra=log_data,
                )
            else:
                logger.debug(
                    f"{operation_name} completed in {duration_ms:.2f}ms",
                    extra=log_data,
                )

    @staticmethod
    def timed(threshold_ms: float = 200.0):
        """
        Decorator to track function execution time.

        Args:
            threshold_ms: Log warning if exceeds this threshold

        Example:
            @PerformanceMonitor.timed(threshold_ms=100)
            async def fetch_recipe(recipe_id):
                return await db.get_recipe(recipe_id)
        """

        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    duration_ms = (time.time() - start_time) * 1000
                    log_data = {
                        "function": func.__name__,
                        "duration_ms": round(duration_ms, 2),
                    }

                    if duration_ms > threshold_ms:
                        logger.warning(
                            f"SLOW FUNCTION: {func.__name__} took {duration_ms:.2f}ms",
                            extra=log_data,
                        )
                    else:
                        logger.debug(
                            f"{func.__name__} completed in {duration_ms:.2f}ms",
                            extra=log_data,
                        )

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration_ms = (time.time() - start_time) * 1000
                    log_data = {
                        "function": func.__name__,
                        "duration_ms": round(duration_ms, 2),
                    }

                    if duration_ms > threshold_ms:
                        logger.warning(
                            f"SLOW FUNCTION: {func.__name__} took {duration_ms:.2f}ms",
                            extra=log_data,
                        )
                    else:
                        logger.debug(
                            f"{func.__name__} completed in {duration_ms:.2f}ms",
                            extra=log_data,
                        )

            import asyncio

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator


class SystemMonitor:
    """Monitor overall system health"""

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """
        Get comprehensive system information.

        Returns:
            Dict with CPU, memory, disk usage
        """
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total_mb": psutil.virtual_memory().total / 1024 / 1024,
                "available_mb": psutil.virtual_memory().available / 1024 / 1024,
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {
                "total_gb": psutil.disk_usage("/").total / 1024 / 1024 / 1024,
                "used_gb": psutil.disk_usage("/").used / 1024 / 1024 / 1024,
                "percent": psutil.disk_usage("/").percent,
            },
            "process": {
                "threads": len(psutil.Process(os.getpid()).threads()),
                "connections": len(psutil.Process(os.getpid()).connections()),
            },
        }

    @staticmethod
    def log_system_health() -> None:
        """Log current system health metrics"""
        info = SystemMonitor.get_system_info()

        logger.info(
            f"System Health - CPU: {info['cpu_percent']}%, "
            f"Memory: {info['memory']['percent']}%, "
            f"Disk: {info['disk']['percent']}%",
            extra=info,
        )


class DatabaseMonitor:
    """Monitor database performance (SQLite specific)"""

    def __init__(self):
        self.query_count = 0
        self.slow_query_count = 0
        self.total_query_time = 0.0

    def record_query(self, duration_ms: float, threshold_ms: float = 100.0) -> None:
        """
        Record a database query execution.

        Args:
            duration_ms: Query execution time in milliseconds
            threshold_ms: Threshold for slow query warning
        """
        self.query_count += 1
        self.total_query_time += duration_ms

        if duration_ms > threshold_ms:
            self.slow_query_count += 1
            logger.warning(
                f"Slow database query: {duration_ms:.2f}ms",
                extra={"duration_ms": duration_ms, "threshold_ms": threshold_ms},
            )

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database performance statistics.

        Returns:
            Dict with query counts and timing
        """
        avg_time = (
            self.total_query_time / self.query_count if self.query_count > 0 else 0
        )

        return {
            "query_count": self.query_count,
            "slow_query_count": self.slow_query_count,
            "total_time_ms": round(self.total_query_time, 2),
            "average_time_ms": round(avg_time, 2),
        }

    def reset_stats(self) -> None:
        """Reset all statistics"""
        self.query_count = 0
        self.slow_query_count = 0
        self.total_query_time = 0.0


# Global monitoring instances
db_monitor = DatabaseMonitor()


def get_all_stats() -> Dict[str, Any]:
    """
    Get all monitoring statistics.

    Returns:
        Dict with memory, system, and database stats
    """
    return {
        "memory": MemoryMonitor.get_memory_info(),
        "system": SystemMonitor.get_system_info(),
        "database": db_monitor.get_stats(),
    }
