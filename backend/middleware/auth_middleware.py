"""
認証ミドルウェア

特定のエンドポイントを除外した API Key 認証を実装。
CLAUDE.md セクション 5.1, 5.3 に準拠。
"""

import os
from typing import List
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv

load_dotenv()


class AuthMiddleware(BaseHTTPMiddleware):
    """
    API Key 認証ミドルウェア

    認証不要のエンドポイント（/health, /docs など）を除外し、
    それ以外のエンドポイントに対して Bearer Token 認証を強制する。
    """

    def __init__(self, app, excluded_paths: List[str] = None):
        """
        Args:
          app: FastAPI アプリケーション
          excluded_paths: 認証除外パス（デフォルト: /health, /docs, /openapi.json, /redoc）
        """
        super().__init__(app)
        self.api_key = os.getenv("API_KEY")

        if not self.api_key:
            raise ValueError(
                "API_KEY environment variable is not set. "
                "Please configure .env file with API_KEY."
            )

        # 認証除外パス
        self.excluded_paths = excluded_paths or [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/",
        ]

    def _is_excluded_path(self, path: str) -> bool:
        """
        パスが認証除外対象か判定する。

        Args:
          path: リクエストパス

        Returns:
          bool: 除外対象の場合 True
        """
        return any(path.startswith(excluded) for excluded in self.excluded_paths)

    def _mask_token(self, token: str) -> str:
        """
        トークンをマスキングする（ログ出力用）。

        Args:
          token: API Key トークン

        Returns:
          str: マスキングされたトークン
        """
        if len(token) <= 6:
            return "***"
        return f"{token[:3]}***{token[-3:]}"

    async def dispatch(self, request: Request, call_next):
        """
        リクエストごとに API Key を検証する。

        Args:
          request: FastAPI Request
          call_next: 次のミドルウェア/ハンドラ

        Returns:
          Response: レスポンス

        Raises:
          HTTPException: 認証失敗時 401 エラー
        """
        # 認証除外パスはスキップ
        if self._is_excluded_path(request.url.path):
            return await call_next(request)

        # Authorization ヘッダー取得
        authorization: str = request.headers.get("Authorization")

        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "data": None,
                    "error": "Missing Authorization header",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Bearer スキーム検証
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "data": None,
                    "error": "Invalid authentication scheme. Use 'Bearer <token>'",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = parts[1]

        # API Key 検証
        if token != self.api_key:
            # セキュリティ: ログに実際のトークンを出力しない
            masked_token = self._mask_token(token)
            print(f"[AUTH] Invalid API Key attempt: {masked_token}")

            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "data": None,
                    "error": "Invalid API Key",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 認証成功
        response = await call_next(request)
        return response
