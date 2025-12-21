"""
Performance and monitoring middleware for Personal Recipe Intelligence
Implements timing, logging, and performance tracking per CLAUDE.md requirements
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track API response times and log slow requests.
    Target: < 200ms per CLAUDE.md Section 12.1
    """

    def __init__(self, app, threshold_ms: float = 200.0):
        super().__init__(app)
        self.threshold_seconds = threshold_ms / 1000.0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time
        duration_ms = duration * 1000

        # Add response header
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

        # Log request details
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "duration_ms": round(duration_ms, 2),
            "status_code": response.status_code,
            "client": request.client.host if request.client else "unknown",
        }

        # Log slow requests (exceeds threshold)
        if duration > self.threshold_seconds:
            logger.warning(
                f"SLOW REQUEST: {request.method} {request.url.path} "
                f"took {duration_ms:.2f}ms (threshold: {self.threshold_seconds * 1000}ms)",
                extra=log_data,
            )
        else:
            logger.info(
                f"{request.method} {request.url.path} - {duration_ms:.2f}ms",
                extra=log_data,
            )

        return response


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all errors with context per CLAUDE.md Section 6
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                    "client": request.client.host if request.client else "unknown",
                },
                exc_info=True,
            )
            raise


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests (audit trail per CLAUDE.md Section 6.4)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log incoming request
        logger.info(
            f"Incoming: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client": request.client.host if request.client else "unknown",
            },
        )

        response = await call_next(request)
        return response
