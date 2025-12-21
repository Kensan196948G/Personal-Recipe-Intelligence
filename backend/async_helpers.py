"""
Async operation helpers for Personal Recipe Intelligence
Utilities to prevent blocking operations in async code
Per CLAUDE.md Section 12.3: async optimization where beneficial
"""

import asyncio
import aiofiles
import json
from typing import Any, Dict, Callable, List, TypeVar, Optional
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Type variable for generic return type
T = TypeVar("T")

# Thread pool for CPU-bound operations (limited size for personal app)
_cpu_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="cpu_bound")
_io_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="io_bound")


async def run_in_thread(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Run a synchronous function in a thread pool to avoid blocking event loop.

    Args:
        func: Synchronous function to run
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Result of func

    Example:
        result = await run_in_thread(blocking_function, arg1, arg2)
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_io_executor, lambda: func(*args, **kwargs))


async def run_cpu_bound(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Run a CPU-intensive function in a dedicated thread pool.

    Args:
        func: CPU-intensive function to run
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Result of func

    Example:
        # OCR processing
        text = await run_cpu_bound(pytesseract.image_to_string, image)
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_cpu_executor, lambda: func(*args, **kwargs))


def async_with_thread_pool(executor_type: str = "io"):
    """
    Decorator to automatically run sync functions in thread pool.

    Args:
        executor_type: "io" for I/O bound or "cpu" for CPU bound

    Example:
        @async_with_thread_pool(executor_type="cpu")
        def expensive_parsing(html):
            # CPU-intensive work
            return parse_html(html)

        # Can now be awaited
        result = await expensive_parsing(html_content)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if executor_type == "cpu":
                return await run_cpu_bound(func, *args, **kwargs)
            else:
                return await run_in_thread(func, *args, **kwargs)

        return wrapper

    return decorator


async def gather_with_timeout(
    *tasks: asyncio.Task, timeout: float, return_exceptions: bool = True
) -> List[Any]:
    """
    Gather multiple tasks with a timeout.

    Args:
        *tasks: Async tasks to gather
        timeout: Timeout in seconds
        return_exceptions: Whether to return exceptions or raise

    Returns:
        List of results

    Example:
        results = await gather_with_timeout(
            fetch_recipe(url1),
            fetch_recipe(url2),
            timeout=10.0
        )
    """
    try:
        return await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=return_exceptions), timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.warning(f"gather_with_timeout exceeded {timeout}s")
        # Cancel remaining tasks
        for task in tasks:
            if not task.done():
                task.cancel()
        raise


async def batch_process(
    items: List[T],
    process_func: Callable[[T], Any],
    batch_size: int = 10,
    max_concurrent: int = 5,
) -> List[Any]:
    """
    Process items in batches with concurrency control.

    Args:
        items: List of items to process
        process_func: Async function to process each item
        batch_size: Number of items per batch
        max_concurrent: Maximum concurrent operations

    Returns:
        List of results

    Example:
        results = await batch_process(
            recipe_urls,
            scrape_recipe,
            batch_size=10,
            max_concurrent=3
        )
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_semaphore(item):
        async with semaphore:
            return await process_func(item)

    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        logger.info(
            f"Processing batch {i // batch_size + 1} "
            f"({len(batch)} items, max concurrent: {max_concurrent})"
        )

        batch_results = await asyncio.gather(
            *[process_with_semaphore(item) for item in batch], return_exceptions=True
        )
        results.extend(batch_results)

    return results


class AsyncFileHandler:
    """
    Async file operations to prevent blocking event loop.
    Per CLAUDE.md: Use async for file I/O where beneficial
    """

    @staticmethod
    async def read_json(file_path: str) -> Dict[str, Any]:
        """
        Async read JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Parsed JSON data
        """
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)

    @staticmethod
    async def write_json(file_path: str, data: Dict[str, Any], indent: int = 2) -> None:
        """
        Async write JSON file.

        Args:
            file_path: Path to JSON file
            data: Data to write
            indent: JSON indentation
        """
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, indent=indent, ensure_ascii=False))

    @staticmethod
    async def read_text(file_path: str) -> str:
        """
        Async read text file.

        Args:
            file_path: Path to text file

        Returns:
            File content
        """
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            return await f.read()

    @staticmethod
    async def write_text(file_path: str, content: str) -> None:
        """
        Async write text file.

        Args:
            file_path: Path to text file
            content: Content to write
        """
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)

    @staticmethod
    async def append_text(file_path: str, content: str) -> None:
        """
        Async append to text file.

        Args:
            file_path: Path to text file
            content: Content to append
        """
        async with aiofiles.open(file_path, "a", encoding="utf-8") as f:
            await f.write(content)

    @staticmethod
    async def read_lines(file_path: str) -> List[str]:
        """
        Async read file lines.

        Args:
            file_path: Path to text file

        Returns:
            List of lines
        """
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            return await f.readlines()


class AsyncRetry:
    """
    Retry async operations with exponential backoff.
    """

    @staticmethod
    async def retry_with_backoff(
        func: Callable,
        *args,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,),
        **kwargs,
    ) -> Any:
        """
        Retry an async function with exponential backoff.

        Args:
            func: Async function to retry
            *args: Positional arguments for func
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            backoff_factor: Multiplier for delay on each retry
            exceptions: Tuple of exceptions to catch
            **kwargs: Keyword arguments for func

        Returns:
            Result of func

        Example:
            result = await AsyncRetry.retry_with_backoff(
                fetch_recipe,
                url,
                max_retries=3,
                initial_delay=1.0
            )
        """
        delay = initial_delay

        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                if attempt == max_retries - 1:
                    logger.error(
                        f"Failed after {max_retries} attempts: {str(e)}",
                        exc_info=True,
                    )
                    raise

                logger.warning(
                    f"Attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}"
                )
                await asyncio.sleep(delay)
                delay *= backoff_factor


class RateLimiter:
    """
    Rate limiter for async operations.
    Useful for web scraping to avoid overwhelming servers.
    """

    def __init__(self, max_requests: int, time_window: float):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.semaphore = asyncio.Semaphore(max_requests)
        self.request_times: List[float] = []

    async def acquire(self):
        """Acquire rate limit slot"""
        async with self.semaphore:
            now = asyncio.get_event_loop().time()

            # Remove old request times
            self.request_times = [
                t for t in self.request_times if now - t < self.time_window
            ]

            # If at limit, wait
            if len(self.request_times) >= self.max_requests:
                sleep_time = self.time_window - (now - self.request_times[0])
                if sleep_time > 0:
                    logger.debug(f"Rate limit reached, sleeping {sleep_time:.2f}s")
                    await asyncio.sleep(sleep_time)
                    self.request_times.pop(0)

            self.request_times.append(now)

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


# Example usage functions


async def example_parallel_scraping(urls: List[str]) -> List[Dict]:
    """
    Example: Scrape multiple URLs in parallel with rate limiting.

    Args:
        urls: List of URLs to scrape

    Returns:
        List of scraped data
    """
    rate_limiter = RateLimiter(max_requests=3, time_window=1.0)  # 3 req/sec

    async def scrape_with_limit(url):
        async with rate_limiter:
            # Your scraping logic here
            logger.info(f"Scraping {url}")
            await asyncio.sleep(0.5)  # Simulate work
            return {"url": url, "status": "success"}

    return await asyncio.gather(*[scrape_with_limit(url) for url in urls])


async def example_cpu_intensive_processing(images: List[str]) -> List[str]:
    """
    Example: Process images with OCR in parallel using thread pool.

    Args:
        images: List of image paths

    Returns:
        List of extracted text
    """

    @async_with_thread_pool(executor_type="cpu")
    def process_single_image(image_path):
        # Simulate CPU-intensive OCR
        # import pytesseract
        # from PIL import Image
        # return pytesseract.image_to_string(Image.open(image_path))
        return f"Text from {image_path}"

    # Process with concurrency control
    results = await batch_process(
        images, process_single_image, batch_size=5, max_concurrent=2
    )

    return results


# Cleanup function for executors
def cleanup_executors():
    """Shutdown thread pool executors"""
    _cpu_executor.shutdown(wait=True)
    _io_executor.shutdown(wait=True)
    logger.info("Thread pool executors shut down")
