"""
API Key Authentication Middleware

APIキー認証とレート制限を行うミドルウェア
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable
import time

from backend.services.api_key_service import APIKeyService


class APIKeyMiddleware:
  """
  APIキー認証ミドルウェア

  機能:
  - APIキー検証
  - レート制限チェック
  - 使用量記録
  """

  def __init__(self, api_key_service: APIKeyService):
    """
    初期化

    Args:
      api_key_service: APIキーサービス
    """
    self.api_key_service = api_key_service

  async def __call__(
    self,
    request: Request,
    call_next: Callable
  ):
    """
    ミドルウェア処理

    Args:
      request: リクエスト
      call_next: 次のハンドラ

    Returns:
      レスポンス
    """
    # 公開エンドポイントのパス
    public_paths = [
      "/api/v1/public/keys",
      "/api/v1/public/docs",
      "/docs",
      "/openapi.json",
      "/health"
    ]

    # 公開パスはスキップ
    if any(request.url.path.startswith(path) for path in public_paths):
      return await call_next(request)

    # APIキーを取得（ヘッダーから）
    api_key = request.headers.get("X-API-Key")
    if not api_key:
      # Authorizationヘッダーからも試す（Bearer形式）
      auth = request.headers.get("Authorization")
      if auth and auth.startswith("Bearer "):
        api_key = auth[7:]

    if not api_key:
      return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
          "status": "error",
          "error": "API key is required",
          "data": None
        }
      )

    # APIキーを検証
    key_info = self.api_key_service.verify_api_key(api_key)
    if not key_info:
      return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
          "status": "error",
          "error": "Invalid API key",
          "data": None
        }
      )

    # レート制限チェック
    is_allowed, error_msg = self.api_key_service.check_rate_limit(
      key_info.key_id
    )
    if not is_allowed:
      return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
          "status": "error",
          "error": error_msg,
          "data": None
        }
      )

    # スコープチェック（エンドポイントに応じて）
    if not self._check_endpoint_scope(request, key_info):
      return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
          "status": "error",
          "error": "Insufficient permissions",
          "data": None
        }
      )

    # リクエストにキー情報を追加
    request.state.api_key_id = key_info.key_id
    request.state.api_key_scope = key_info.scope

    # リクエストを処理
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    # 使用量を記録
    self.api_key_service.record_usage(
      key_id=key_info.key_id,
      endpoint=request.url.path,
      status_code=response.status_code
    )

    # レート制限情報をヘッダーに追加
    stats = self.api_key_service.get_usage_stats(key_info.key_id)
    if stats:
      response.headers["X-RateLimit-Limit-Minute"] = str(
        stats["rate_limits"]["per_minute"]
      )
      response.headers["X-RateLimit-Remaining-Minute"] = str(
        max(0, stats["remaining"]["per_minute"])
      )
      response.headers["X-RateLimit-Limit-Hour"] = str(
        stats["rate_limits"]["per_hour"]
      )
      response.headers["X-RateLimit-Remaining-Hour"] = str(
        max(0, stats["remaining"]["per_hour"])
      )

    # 処理時間をヘッダーに追加
    response.headers["X-Response-Time"] = f"{duration:.3f}s"

    return response

  def _check_endpoint_scope(self, request: Request, key_info) -> bool:
    """
    エンドポイントに対するスコープをチェック

    Args:
      request: リクエスト
      key_info: APIキー情報

    Returns:
      アクセス可能かどうか
    """
    method = request.method
    path = request.url.path

    # レシピエンドポイント
    if "/recipes" in path:
      if method == "GET":
        return key_info.scope.read_recipes
      elif method in ["POST", "PUT", "PATCH"]:
        return key_info.scope.write_recipes
      elif method == "DELETE":
        return key_info.scope.delete_recipes

    # タグエンドポイント
    if "/tags" in path:
      if method == "GET":
        return key_info.scope.read_tags
      elif method in ["POST", "PUT", "PATCH", "DELETE"]:
        return key_info.scope.write_tags

    # デフォルトは読み取り権限のみ
    if method == "GET":
      return key_info.scope.read_recipes or key_info.scope.read_tags

    return False


def require_scope(required_scope: str):
  """
  特定のスコープを要求するデコレーター

  Args:
    required_scope: 必要なスコープ名

  Returns:
    デコレーター関数
  """
  def decorator(func):
    async def wrapper(request: Request, *args, **kwargs):
      # リクエストからスコープを取得
      if not hasattr(request.state, "api_key_scope"):
        raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="API key required"
        )

      scope = request.state.api_key_scope
      if not getattr(scope, required_scope, False):
        raise HTTPException(
          status_code=status.HTTP_403_FORBIDDEN,
          detail=f"Required scope: {required_scope}"
        )

      return await func(request, *args, **kwargs)

    return wrapper
  return decorator
