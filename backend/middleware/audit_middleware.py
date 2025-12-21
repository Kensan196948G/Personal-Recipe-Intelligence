"""
Audit Middleware for Personal Recipe Intelligence

認証・認可時の監査ログ自動記録
"""

from functools import wraps
from typing import Callable, Optional
from flask import Request, request, g
from backend.services.audit_service import get_audit_service


def get_client_ip(req: Request) -> str:
  """
  クライアントIPアドレスを取得

  Args:
      req: Flaskリクエストオブジェクト

  Returns:
      IPアドレス文字列
  """
  # X-Forwarded-For ヘッダーを優先（プロキシ経由の場合）
  if req.headers.get("X-Forwarded-For"):
    return req.headers.get("X-Forwarded-For").split(",")[0].strip()
  elif req.headers.get("X-Real-IP"):
    return req.headers.get("X-Real-IP")
  else:
    return req.remote_addr or "unknown"


def audit_auth_attempt(func: Callable) -> Callable:
  """
  認証試行を監査ログに記録するデコレータ

  認証成功時と失敗時の両方を記録

  Args:
      func: デコレート対象の関数

  Returns:
      ラップされた関数
  """

  @wraps(func)
  def wrapper(*args, **kwargs):
    audit_service = get_audit_service()
    ip_address = get_client_ip(request)

    try:
      result = func(*args, **kwargs)

      # 認証成功（user_id を g から取得）
      user_id = getattr(g, "user_id", None)
      if user_id:
        audit_service.log_auth_success(
          user_id=user_id, ip_address=ip_address, method="api_key"
        )

      return result

    except Exception as e:
      # 認証失敗
      user_id = getattr(g, "user_id", None)
      audit_service.log_auth_failure(
        user_id=user_id, ip_address=ip_address, reason=str(e), method="api_key"
      )
      raise

  return wrapper


def audit_api_call(resource_type: str = "system"):
  """
  API呼び出しを監査ログに記録するデコレータファクトリ

  Args:
      resource_type: リソースタイプ（recipe, user, など）

  Returns:
      デコレータ関数
  """

  def decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
      # API呼び出し情報を収集
      ip_address = get_client_ip(request)
      user_id = getattr(g, "user_id", None)

      # 実行
      result = func(*args, **kwargs)

      # ここでは詳細なログは各エンドポイントで個別に記録するため
      # このデコレータは将来的な拡張用として保持

      return result

    return wrapper

  return decorator


class AuditContext:
  """
  監査コンテキストマネージャ

  with文で監査ログを自動記録
  """

  def __init__(
    self,
    action: str,
    resource_type: str,
    user_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
  ):
    """
    初期化

    Args:
        action: アクション名
        resource_type: リソースタイプ
        user_id: ユーザーID
        resource_id: リソースID
        ip_address: IPアドレス
    """
    self.action = action
    self.resource_type = resource_type
    self.user_id = user_id
    self.resource_id = resource_id
    self.ip_address = ip_address or get_client_ip(request)
    self.audit_service = get_audit_service()
    self.details = {}

  def __enter__(self):
    """コンテキスト開始"""
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    """
    コンテキスト終了

    成功時または失敗時のログを記録
    """
    if exc_type is None:
      # 成功
      status = "success"
    else:
      # 失敗
      status = "failure"
      self.details["error"] = str(exc_val)

    # 監査ログに記録（内部でEnum変換は不要なため直接記録）
    # 実際にはAuditServiceの専用メソッドを使用することを推奨
    self.audit_service.logger.info(
      f"Audit Context: {self.action} on {self.resource_type} "
      f"by user={self.user_id} status={status}"
    )

  def add_detail(self, key: str, value: any) -> "AuditContext":
    """
    詳細情報を追加

    Args:
        key: キー
        value: 値

    Returns:
        自身（チェーン可能）
    """
    self.details[key] = value
    return self


def extract_user_id_from_request() -> Optional[str]:
  """
  リクエストからユーザーIDを抽出

  Flask g オブジェクトから取得

  Returns:
      ユーザーID（存在しない場合はNone）
  """
  return getattr(g, "user_id", None)
