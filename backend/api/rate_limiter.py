"""
Rate Limiter for Personal Recipe Intelligence API

シンプルで軽量なレートリミッター実装。
SlowAPI の代わりに、メモリベースの自作実装を使用。
"""

import time
from typing import Dict, Optional, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException, status
import asyncio


class RateLimiter:
    """
    メモリベースのシンプルなレートリミッター。

    IPアドレスごとにリクエスト数をトラッキングし、
    制限を超えた場合は429エラーを返す。
    """

    def __init__(self):
        """レートリミッターの初期化"""
        # {ip_address: {endpoint: [(timestamp, count)]}}
        self._requests: Dict[str, Dict[str, list]] = defaultdict(
            lambda: defaultdict(list)
        )
        # クリーンアップ用のロック
        self._lock = asyncio.Lock()
        # 最後のクリーンアップ時刻
        self._last_cleanup = time.time()
        # クリーンアップ間隔（秒）
        self._cleanup_interval = 300  # 5分

    async def _cleanup_old_entries(self):
        """
        古いエントリをクリーンアップしてメモリ使用量を削減。
        """
        current_time = time.time()

        # クリーンアップ間隔チェック
        if current_time - self._last_cleanup < self._cleanup_interval:
            return

        async with self._lock:
            # 1時間以上前のエントリを削除
            cutoff_time = current_time - 3600

            for ip in list(self._requests.keys()):
                for endpoint in list(self._requests[ip].keys()):
                    # 古いタイムスタンプを削除
                    self._requests[ip][endpoint] = [
                        (ts, count)
                        for ts, count in self._requests[ip][endpoint]
                        if ts > cutoff_time
                    ]

                    # 空のエンドポイントを削除
                    if not self._requests[ip][endpoint]:
                        del self._requests[ip][endpoint]

                # 空のIPエントリを削除
                if not self._requests[ip]:
                    del self._requests[ip]

            self._last_cleanup = current_time

    async def check_rate_limit(
        self, ip_address: str, endpoint: str, limit: int, window: int = 60
    ) -> Tuple[bool, Optional[int]]:
        """
        レートリミットをチェック。

        Args:
          ip_address: クライアントのIPアドレス
          endpoint: エンドポイント名
          limit: 許可されるリクエスト数
          window: 時間窓（秒）

        Returns:
          (許可されるか, リトライまでの秒数)
        """
        current_time = time.time()
        cutoff_time = current_time - window

        # 定期的なクリーンアップ
        await self._cleanup_old_entries()

        # 現在の窓内のリクエストを取得
        requests = self._requests[ip_address][endpoint]

        # 古いリクエストを削除
        valid_requests = [(ts, count) for ts, count in requests if ts > cutoff_time]

        # リクエスト数をカウント
        total_requests = sum(count for _, count in valid_requests)

        if total_requests >= limit:
            # 最も古いリクエストからのリトライ時間を計算
            if valid_requests:
                oldest_timestamp = min(ts for ts, _ in valid_requests)
                retry_after = int(window - (current_time - oldest_timestamp)) + 1
            else:
                retry_after = window

            return False, retry_after

        # 新しいリクエストを記録
        valid_requests.append((current_time, 1))
        self._requests[ip_address][endpoint] = valid_requests

        return True, None

    def get_client_ip(self, request: Request) -> str:
        """
        リクエストからクライアントIPを取得。

        Args:
          request: FastAPI Request オブジェクト

        Returns:
          クライアントIPアドレス
        """
        # X-Forwarded-For ヘッダーをチェック（プロキシ経由の場合）
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # X-Real-IP ヘッダーをチェック
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 直接接続の場合
        if request.client:
            return request.client.host

        return "unknown"


# グローバルなレートリミッターインスタンス
rate_limiter = RateLimiter()


class RateLimitConfig:
    """レートリミット設定の定義"""

    # 一般API: 60リクエスト/分
    GENERAL = {"limit": 60, "window": 60}

    # OCR: 10リクエスト/分
    OCR = {"limit": 10, "window": 60}

    # Translation: 30リクエスト/分
    TRANSLATION = {"limit": 30, "window": 60}

    # Scraper: 20リクエスト/分
    SCRAPER = {"limit": 20, "window": 60}


async def rate_limit_dependency(
    request: Request,
    limit: int = 60,
    window: int = 60,
    endpoint_name: Optional[str] = None,
):
    """
    FastAPI の依存性注入として使用するレートリミッター。

    Args:
      request: FastAPI Request
      limit: リクエスト制限数
      window: 時間窓（秒）
      endpoint_name: エンドポイント名（Noneの場合はパスを使用）

    Raises:
      HTTPException: レートリミット超過時
    """
    ip_address = rate_limiter.get_client_ip(request)
    endpoint = endpoint_name or request.url.path

    allowed, retry_after = await rate_limiter.check_rate_limit(
        ip_address=ip_address, endpoint=endpoint, limit=limit, window=window
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "status": "error",
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"レートリミットを超過しました。{retry_after}秒後に再試行してください。",
                    "retry_after": retry_after,
                },
                "data": None,
            },
            headers={"Retry-After": str(retry_after)},
        )


def create_rate_limit_dependency(
    limit: int, window: int = 60, endpoint_name: Optional[str] = None
):
    """
    カスタムレートリミット設定を持つ依存性を作成。

    Args:
      limit: リクエスト制限数
      window: 時間窓（秒）
      endpoint_name: エンドポイント名

    Returns:
      依存性関数
    """

    async def dependency(request: Request):
        await rate_limit_dependency(request, limit, window, endpoint_name)

    return dependency


# 各エンドポイント用の依存性を事前定義
general_rate_limit = create_rate_limit_dependency(
    **RateLimitConfig.GENERAL, endpoint_name="general"
)

ocr_rate_limit = create_rate_limit_dependency(
    **RateLimitConfig.OCR, endpoint_name="ocr"
)

translation_rate_limit = create_rate_limit_dependency(
    **RateLimitConfig.TRANSLATION, endpoint_name="translation"
)

scraper_rate_limit = create_rate_limit_dependency(
    **RateLimitConfig.SCRAPER, endpoint_name="scraper"
)
