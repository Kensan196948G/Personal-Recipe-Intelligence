"""
API Key 認証モジュール

Bearer Token 形式の API Key 検証を提供する。
CLAUDE.md セクション 5.1, 5.2, 5.3 に準拠。
"""

import os
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# HTTPBearer スキーム（Bearer Token 形式）
security = HTTPBearer()


class APIKeyAuth:
    """API Key 認証クラス"""

    def __init__(self):
        """
        環境変数から API_KEY を読み込む。
        API_KEY が未設定の場合は警告を出す。
        """
        self.api_key: Optional[str] = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError(
                "API_KEY environment variable is not set. "
                "Please configure .env file with API_KEY."
            )

    def verify_api_key(
        self, credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> bool:
        """
        API Key を検証する。

        Args:
          credentials: HTTPAuthorizationCredentials（Bearer Token）

        Returns:
          bool: 認証成功時 True

        Raises:
          HTTPException: 認証失敗時 401 エラー
        """
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use Bearer token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if credentials.credentials != self.api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return True

    def mask_api_key(self, key: str) -> str:
        """
        API Key をマスキングする（ログ出力用）。

        Args:
          key: API Key 文字列

        Returns:
          str: マスキングされた文字列（例: "abc***xyz"）
        """
        if len(key) <= 6:
            return "***"
        return f"{key[:3]}***{key[-3:]}"


# グローバルインスタンス
api_key_auth = APIKeyAuth()


def get_api_key_auth() -> bool:
    """
    FastAPI の Depends で使用する認証関数。

    Returns:
      bool: 認証成功時 True

    Raises:
      HTTPException: 認証失敗時 401 エラー

    Usage:
      @app.get("/api/v1/recipes", dependencies=[Depends(get_api_key_auth)])
      async def get_recipes():
        ...
    """
    return api_key_auth.verify_api_key()
