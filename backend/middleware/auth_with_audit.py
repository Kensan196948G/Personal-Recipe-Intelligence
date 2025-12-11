"""
Authentication Middleware with Audit Logging

認証ミドルウェア + 監査ログ統合
CLAUDE.md Section 5.1, 6.4 準拠
"""

from functools import wraps
from typing import Callable, Optional
from flask import request, jsonify, g
import secrets
import hashlib
from backend.services.audit_service import get_audit_service
from backend.middleware.audit_middleware import get_client_ip


# 監査サービス
audit_service = get_audit_service()


# === API Key Storage (実際にはDBを使用) ===

# 仮のAPIキーストレージ（実際はデータベース）
API_KEYS = {
  "user_001": {
    "key_hash": hashlib.sha256("test_api_key_123".encode()).hexdigest(),
    "name": "Test User",
    "active": True,
  }
}


# === Authentication Functions ===


def verify_api_key(api_key: str) -> Optional[str]:
  """
  APIキーを検証

  Args:
      api_key: APIキー文字列

  Returns:
      ユーザーID（検証成功時）、None（失敗時）
  """
  key_hash = hashlib.sha256(api_key.encode()).hexdigest()

  for user_id, key_data in API_KEYS.items():
    if key_data["key_hash"] == key_hash and key_data["active"]:
      return user_id

  return None


def require_auth(func: Callable) -> Callable:
  """
  認証必須デコレータ

  監査ログ統合済み

  Args:
      func: デコレート対象の関数

  Returns:
      ラップされた関数
  """

  @wraps(func)
  def wrapper(*args, **kwargs):
    ip_address = get_client_ip(request)

    # APIキーを取得
    api_key = None
    auth_header = request.headers.get("Authorization")

    if auth_header:
      # Bearer トークン形式
      if auth_header.startswith("Bearer "):
        api_key = auth_header[7:]
      # API-Key ヘッダー形式
      elif auth_header.startswith("API-Key "):
        api_key = auth_header[8:]

    # X-API-Key ヘッダーもサポート
    if not api_key:
      api_key = request.headers.get("X-API-Key")

    # APIキーが存在しない
    if not api_key:
      audit_service.log_auth_failure(
        user_id=None, ip_address=ip_address, reason="missing_api_key", method="api_key"
      )
      return jsonify({"status": "error", "error": "API key required"}), 401

    # APIキーを検証
    user_id = verify_api_key(api_key)

    if not user_id:
      # 検証失敗 - トークンの最初の8文字のみ記録（セキュリティ）
      token_prefix = api_key[:8] if len(api_key) >= 8 else api_key
      audit_service.log_auth_failure(
        user_id=None, ip_address=ip_address, reason="invalid_api_key", method="api_key"
      )
      audit_service.log_invalid_token(
        ip_address=ip_address, token_prefix=token_prefix
      )
      return jsonify({"status": "error", "error": "Invalid API key"}), 401

    # 認証成功
    g.user_id = user_id
    audit_service.log_auth_success(
      user_id=user_id, ip_address=ip_address, method="api_key"
    )

    # 実際の関数を実行
    return func(*args, **kwargs)

  return wrapper


def optional_auth(func: Callable) -> Callable:
  """
  認証オプショナルデコレータ

  認証情報があれば検証し、なければそのまま実行

  Args:
      func: デコレート対象の関数

  Returns:
      ラップされた関数
  """

  @wraps(func)
  def wrapper(*args, **kwargs):
    ip_address = get_client_ip(request)

    # APIキーを取得
    api_key = None
    auth_header = request.headers.get("Authorization")

    if auth_header:
      if auth_header.startswith("Bearer "):
        api_key = auth_header[7:]
      elif auth_header.startswith("API-Key "):
        api_key = auth_header[8:]

    if not api_key:
      api_key = request.headers.get("X-API-Key")

    # APIキーがあれば検証
    if api_key:
      user_id = verify_api_key(api_key)
      if user_id:
        g.user_id = user_id
        audit_service.log_auth_success(
          user_id=user_id, ip_address=ip_address, method="api_key"
        )
      else:
        # 無効なキーでもエラーにせず実行（オプショナル認証）
        token_prefix = api_key[:8] if len(api_key) >= 8 else api_key
        audit_service.log_invalid_token(
          ip_address=ip_address, token_prefix=token_prefix
        )

    # 実際の関数を実行
    return func(*args, **kwargs)

  return wrapper


# === API Key Management with Audit Logging ===


def create_api_key(user_id: str, key_name: Optional[str] = None) -> str:
  """
  APIキーを生成

  監査ログ記録済み

  Args:
      user_id: ユーザーID
      key_name: キー名（オプション）

  Returns:
      生成されたAPIキー
  """
  ip_address = get_client_ip(request) if request else None

  # 新しいAPIキーを生成
  api_key = f"pri_{secrets.token_urlsafe(32)}"
  key_hash = hashlib.sha256(api_key.encode()).hexdigest()

  # キーIDを生成
  key_id = hashlib.sha256(f"{user_id}_{api_key}".encode()).hexdigest()[:16]

  # ストレージに保存（実際はDB）
  API_KEYS[user_id] = {
    "key_hash": key_hash,
    "name": key_name or "Default Key",
    "active": True,
    "key_id": key_id,
  }

  # 監査ログ記録
  audit_service.log_api_key_created(
    user_id=user_id, key_id=key_id, ip_address=ip_address, key_name=key_name
  )

  return api_key


def revoke_api_key(user_id: str, key_id: str) -> bool:
  """
  APIキーを失効

  監査ログ記録済み

  Args:
      user_id: ユーザーID
      key_id: キーID

  Returns:
      成功時True
  """
  ip_address = get_client_ip(request) if request else None

  # キーを失効（実際はDB更新）
  if user_id in API_KEYS:
    key_name = API_KEYS[user_id].get("name")
    API_KEYS[user_id]["active"] = False

    # 監査ログ記録
    audit_service.log_api_key_deleted(
      user_id=user_id, key_id=key_id, ip_address=ip_address, key_name=key_name
    )

    return True

  return False


def rotate_api_key(user_id: str, old_key_id: str) -> str:
  """
  APIキーをローテーション（古いキーを失効し新しいキーを生成）

  監査ログ記録済み

  Args:
      user_id: ユーザーID
      old_key_id: 古いキーID

  Returns:
      新しいAPIキー
  """
  ip_address = get_client_ip(request) if request else None

  # 新しいキーを生成
  new_api_key = create_api_key(user_id, key_name="Rotated Key")
  new_key_id = API_KEYS[user_id]["key_id"]

  # 監査ログ記録（ローテーション）
  audit_service.log_api_key_rotated(
    user_id=user_id,
    old_key_id=old_key_id,
    new_key_id=new_key_id,
    ip_address=ip_address,
  )

  return new_api_key


# === Rate Limiting with Audit Logging ===

# 簡易レート制限（実際はRedisなどを使用）
RATE_LIMIT_STORAGE = {}


def check_rate_limit(user_id: str, limit: int = 100, window: int = 60) -> bool:
  """
  レート制限をチェック

  Args:
      user_id: ユーザーID
      limit: 制限回数
      window: 時間窓（秒）

  Returns:
      制限内ならTrue
  """
  import time

  current_time = int(time.time())
  window_start = current_time - window

  # ユーザーのリクエスト履歴を取得
  if user_id not in RATE_LIMIT_STORAGE:
    RATE_LIMIT_STORAGE[user_id] = []

  # 古いリクエストを削除
  RATE_LIMIT_STORAGE[user_id] = [
    t for t in RATE_LIMIT_STORAGE[user_id] if t > window_start
  ]

  # 制限チェック
  if len(RATE_LIMIT_STORAGE[user_id]) >= limit:
    # 制限超過 - 監査ログ記録
    ip_address = get_client_ip(request) if request else None
    audit_service.log_rate_limit_exceeded(
      ip_address=ip_address, user_id=user_id, endpoint=request.path if request else None
    )
    return False

  # リクエストを記録
  RATE_LIMIT_STORAGE[user_id].append(current_time)
  return True


def rate_limit(limit: int = 100, window: int = 60):
  """
  レート制限デコレータ

  Args:
      limit: 制限回数
      window: 時間窓（秒）

  Returns:
      デコレータ
  """

  def decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
      user_id = getattr(g, "user_id", None)

      if user_id and not check_rate_limit(user_id, limit, window):
        return jsonify({"status": "error", "error": "Rate limit exceeded"}), 429

      return func(*args, **kwargs)

    return wrapper

  return decorator
