"""
Audit Service for Personal Recipe Intelligence

監査ログサービス - セキュリティ関連イベントの記録
CLAUDE.md Section 6.4 準拠
"""

import json
import logging
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional
from threading import Lock


class AuditAction(Enum):
  """監査対象アクション"""

  # Recipe CRUD
  RECIPE_CREATE = "recipe_create"
  RECIPE_READ = "recipe_read"
  RECIPE_UPDATE = "recipe_update"
  RECIPE_DELETE = "recipe_delete"
  RECIPE_BATCH_DELETE = "recipe_batch_delete"

  # Authentication
  AUTH_SUCCESS = "auth_success"
  AUTH_FAILURE = "auth_failure"
  AUTH_TOKEN_CREATED = "auth_token_created"
  AUTH_TOKEN_REVOKED = "auth_token_revoked"

  # API Key Operations
  API_KEY_CREATED = "api_key_created"
  API_KEY_DELETED = "api_key_deleted"
  API_KEY_ROTATED = "api_key_rotated"

  # Administrative Actions
  ADMIN_CONFIG_UPDATED = "admin_config_updated"
  ADMIN_USER_CREATED = "admin_user_created"
  ADMIN_USER_DELETED = "admin_user_deleted"
  ADMIN_BACKUP_CREATED = "admin_backup_created"
  ADMIN_RESTORE_EXECUTED = "admin_restore_executed"

  # Data Operations
  DATA_IMPORT = "data_import"
  DATA_EXPORT = "data_export"
  DATA_MIGRATION = "data_migration"

  # Security Events
  SECURITY_BREACH_ATTEMPT = "security_breach_attempt"
  SECURITY_RATE_LIMIT_EXCEEDED = "security_rate_limit_exceeded"
  SECURITY_INVALID_TOKEN = "security_invalid_token"


class AuditResourceType(Enum):
  """監査対象リソースタイプ"""

  RECIPE = "recipe"
  USER = "user"
  API_KEY = "api_key"
  AUTH_TOKEN = "auth_token"
  CONFIG = "config"
  BACKUP = "backup"
  SYSTEM = "system"


class AuditService:
  """
  監査ログサービス

  すべてのセキュリティ関連イベントを記録する
  JSON形式でログファイルに追記
  """

  def __init__(self, log_dir: str = "logs"):
    """
    初期化

    Args:
        log_dir: ログディレクトリパス
    """
    self.log_dir = Path(log_dir)
    self.log_dir.mkdir(parents=True, exist_ok=True)

    self.audit_log_path = self.log_dir / "audit.json"
    self.lock = Lock()  # スレッドセーフな書き込み

    # ロガー設定
    self.logger = logging.getLogger("audit_service")
    self.logger.setLevel(logging.INFO)

    # ファイルハンドラ
    handler = logging.FileHandler(self.log_dir / "audit_service.log")
    handler.setFormatter(
      logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    self.logger.addHandler(handler)

  def log(
    self,
    action: AuditAction,
    resource_type: AuditResourceType,
    user_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    status: str = "success",
  ) -> None:
    """
    監査ログを記録

    Args:
        action: 実行されたアクション
        resource_type: 対象リソースタイプ
        user_id: ユーザーID（オプション）
        resource_id: リソースID（オプション）
        ip_address: IPアドレス（オプション）
        details: 追加詳細情報（オプション）
        status: 実行結果（success/failure）
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
      "timestamp": timestamp,
      "action": action.value,
      "resource_type": resource_type.value,
      "status": status,
      "user_id": user_id,
      "resource_id": resource_id,
      "ip_address": ip_address,
      "details": self._sanitize_details(details) if details else {},
    }

    try:
      with self.lock:
        # JSON形式で追記
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
          json.dump(audit_entry, f, ensure_ascii=False)
          f.write("\n")

      self.logger.info(
        f"Audit: {action.value} on {resource_type.value} "
        f"by user={user_id} status={status}"
      )

    except Exception as e:
      self.logger.error(f"Failed to write audit log: {e}")
      # 監査ログの失敗は致命的なので別途記録
      self._write_emergency_log(audit_entry, e)

  def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    機密データをマスク

    Args:
        details: 詳細情報

    Returns:
        サニタイズされた詳細情報
    """
    sensitive_keys = {
      "password",
      "token",
      "api_key",
      "secret",
      "apikey",
      "auth_token",
      "bearer",
    }

    sanitized = {}
    for key, value in details.items():
      key_lower = key.lower()

      # 機密キーをマスク
      if any(sensitive in key_lower for sensitive in sensitive_keys):
        sanitized[key] = "***MASKED***"
      elif isinstance(value, dict):
        sanitized[key] = self._sanitize_details(value)
      elif isinstance(value, list):
        sanitized[key] = [
          self._sanitize_details(item) if isinstance(item, dict) else item
          for item in value
        ]
      else:
        sanitized[key] = value

    return sanitized

  def _write_emergency_log(
    self, audit_entry: Dict[str, Any], error: Exception
  ) -> None:
    """
    緊急ログを別ファイルに記録

    監査ログの書き込みに失敗した場合の最終手段

    Args:
        audit_entry: 監査エントリ
        error: 発生したエラー
    """
    emergency_log_path = self.log_dir / "audit_emergency.json"
    try:
      with open(emergency_log_path, "a", encoding="utf-8") as f:
        emergency_entry = {
          "timestamp": datetime.now(timezone.utc).isoformat(),
          "error": str(error),
          "original_entry": audit_entry,
        }
        json.dump(emergency_entry, f, ensure_ascii=False)
        f.write("\n")
    except Exception as e:
      # これも失敗したら標準エラー出力
      print(f"CRITICAL: Failed to write emergency audit log: {e}", flush=True)

  # === Recipe CRUD Audit Methods ===

  def log_recipe_create(
    self,
    recipe_id: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    recipe_title: Optional[str] = None,
  ) -> None:
    """レシピ作成を記録"""
    self.log(
      action=AuditAction.RECIPE_CREATE,
      resource_type=AuditResourceType.RECIPE,
      user_id=user_id,
      resource_id=recipe_id,
      ip_address=ip_address,
      details={"recipe_title": recipe_title} if recipe_title else None,
      status="success",
    )

  def log_recipe_update(
    self,
    recipe_id: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    changes: Optional[Dict[str, Any]] = None,
  ) -> None:
    """レシピ更新を記録"""
    self.log(
      action=AuditAction.RECIPE_UPDATE,
      resource_type=AuditResourceType.RECIPE,
      user_id=user_id,
      resource_id=recipe_id,
      ip_address=ip_address,
      details={"changes": changes} if changes else None,
      status="success",
    )

  def log_recipe_delete(
    self,
    recipe_id: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    recipe_title: Optional[str] = None,
  ) -> None:
    """レシピ削除を記録"""
    self.log(
      action=AuditAction.RECIPE_DELETE,
      resource_type=AuditResourceType.RECIPE,
      user_id=user_id,
      resource_id=recipe_id,
      ip_address=ip_address,
      details={"recipe_title": recipe_title} if recipe_title else None,
      status="success",
    )

  def log_recipe_batch_delete(
    self,
    recipe_ids: list[str],
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
  ) -> None:
    """レシピ一括削除を記録"""
    self.log(
      action=AuditAction.RECIPE_BATCH_DELETE,
      resource_type=AuditResourceType.RECIPE,
      user_id=user_id,
      resource_id="batch",
      ip_address=ip_address,
      details={"recipe_ids": recipe_ids, "count": len(recipe_ids)},
      status="success",
    )

  # === Authentication Audit Methods ===

  def log_auth_success(
    self,
    user_id: str,
    ip_address: Optional[str] = None,
    method: str = "api_key",
  ) -> None:
    """認証成功を記録"""
    self.log(
      action=AuditAction.AUTH_SUCCESS,
      resource_type=AuditResourceType.AUTH_TOKEN,
      user_id=user_id,
      ip_address=ip_address,
      details={"method": method},
      status="success",
    )

  def log_auth_failure(
    self,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    reason: str = "invalid_credentials",
    method: str = "api_key",
  ) -> None:
    """認証失敗を記録"""
    self.log(
      action=AuditAction.AUTH_FAILURE,
      resource_type=AuditResourceType.AUTH_TOKEN,
      user_id=user_id,
      ip_address=ip_address,
      details={"reason": reason, "method": method},
      status="failure",
    )

  def log_token_created(
    self,
    user_id: str,
    token_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    expires_at: Optional[str] = None,
  ) -> None:
    """トークン作成を記録"""
    self.log(
      action=AuditAction.AUTH_TOKEN_CREATED,
      resource_type=AuditResourceType.AUTH_TOKEN,
      user_id=user_id,
      resource_id=token_id,
      ip_address=ip_address,
      details={"expires_at": expires_at} if expires_at else None,
      status="success",
    )

  def log_token_revoked(
    self,
    user_id: str,
    token_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    reason: str = "user_request",
  ) -> None:
    """トークン失効を記録"""
    self.log(
      action=AuditAction.AUTH_TOKEN_REVOKED,
      resource_type=AuditResourceType.AUTH_TOKEN,
      user_id=user_id,
      resource_id=token_id,
      ip_address=ip_address,
      details={"reason": reason},
      status="success",
    )

  # === API Key Audit Methods ===

  def log_api_key_created(
    self,
    user_id: str,
    key_id: str,
    ip_address: Optional[str] = None,
    key_name: Optional[str] = None,
  ) -> None:
    """APIキー作成を記録"""
    self.log(
      action=AuditAction.API_KEY_CREATED,
      resource_type=AuditResourceType.API_KEY,
      user_id=user_id,
      resource_id=key_id,
      ip_address=ip_address,
      details={"key_name": key_name} if key_name else None,
      status="success",
    )

  def log_api_key_deleted(
    self,
    user_id: str,
    key_id: str,
    ip_address: Optional[str] = None,
    key_name: Optional[str] = None,
  ) -> None:
    """APIキー削除を記録"""
    self.log(
      action=AuditAction.API_KEY_DELETED,
      resource_type=AuditResourceType.API_KEY,
      user_id=user_id,
      resource_id=key_id,
      ip_address=ip_address,
      details={"key_name": key_name} if key_name else None,
      status="success",
    )

  def log_api_key_rotated(
    self,
    user_id: str,
    old_key_id: str,
    new_key_id: str,
    ip_address: Optional[str] = None,
  ) -> None:
    """APIキーローテーションを記録"""
    self.log(
      action=AuditAction.API_KEY_ROTATED,
      resource_type=AuditResourceType.API_KEY,
      user_id=user_id,
      resource_id=new_key_id,
      ip_address=ip_address,
      details={"old_key_id": old_key_id, "new_key_id": new_key_id},
      status="success",
    )

  # === Administrative Audit Methods ===

  def log_admin_config_updated(
    self,
    user_id: str,
    config_key: str,
    ip_address: Optional[str] = None,
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None,
  ) -> None:
    """設定変更を記録"""
    self.log(
      action=AuditAction.ADMIN_CONFIG_UPDATED,
      resource_type=AuditResourceType.CONFIG,
      user_id=user_id,
      resource_id=config_key,
      ip_address=ip_address,
      details={"old_value": old_value, "new_value": new_value},
      status="success",
    )

  def log_admin_backup_created(
    self,
    user_id: str,
    backup_id: str,
    ip_address: Optional[str] = None,
    backup_size: Optional[int] = None,
  ) -> None:
    """バックアップ作成を記録"""
    self.log(
      action=AuditAction.ADMIN_BACKUP_CREATED,
      resource_type=AuditResourceType.BACKUP,
      user_id=user_id,
      resource_id=backup_id,
      ip_address=ip_address,
      details={"size_bytes": backup_size} if backup_size else None,
      status="success",
    )

  def log_admin_restore_executed(
    self,
    user_id: str,
    backup_id: str,
    ip_address: Optional[str] = None,
  ) -> None:
    """リストア実行を記録"""
    self.log(
      action=AuditAction.ADMIN_RESTORE_EXECUTED,
      resource_type=AuditResourceType.BACKUP,
      user_id=user_id,
      resource_id=backup_id,
      ip_address=ip_address,
      status="success",
    )

  # === Security Event Audit Methods ===

  def log_security_breach_attempt(
    self,
    ip_address: str,
    user_id: Optional[str] = None,
    attack_type: str = "unknown",
    details: Optional[Dict[str, Any]] = None,
  ) -> None:
    """セキュリティ侵害試行を記録"""
    self.log(
      action=AuditAction.SECURITY_BREACH_ATTEMPT,
      resource_type=AuditResourceType.SYSTEM,
      user_id=user_id,
      ip_address=ip_address,
      details={"attack_type": attack_type, **(details or {})},
      status="blocked",
    )

  def log_rate_limit_exceeded(
    self,
    ip_address: str,
    user_id: Optional[str] = None,
    endpoint: Optional[str] = None,
  ) -> None:
    """レート制限超過を記録"""
    self.log(
      action=AuditAction.SECURITY_RATE_LIMIT_EXCEEDED,
      resource_type=AuditResourceType.SYSTEM,
      user_id=user_id,
      ip_address=ip_address,
      details={"endpoint": endpoint} if endpoint else None,
      status="blocked",
    )

  def log_invalid_token(
    self,
    ip_address: str,
    user_id: Optional[str] = None,
    token_prefix: Optional[str] = None,
  ) -> None:
    """無効トークン使用を記録"""
    self.log(
      action=AuditAction.SECURITY_INVALID_TOKEN,
      resource_type=AuditResourceType.AUTH_TOKEN,
      user_id=user_id,
      ip_address=ip_address,
      details={"token_prefix": token_prefix} if token_prefix else None,
      status="rejected",
    )

  # === Data Operation Audit Methods ===

  def log_data_import(
    self,
    user_id: str,
    ip_address: Optional[str] = None,
    record_count: Optional[int] = None,
    source: Optional[str] = None,
  ) -> None:
    """データインポートを記録"""
    self.log(
      action=AuditAction.DATA_IMPORT,
      resource_type=AuditResourceType.SYSTEM,
      user_id=user_id,
      ip_address=ip_address,
      details={"record_count": record_count, "source": source},
      status="success",
    )

  def log_data_export(
    self,
    user_id: str,
    ip_address: Optional[str] = None,
    record_count: Optional[int] = None,
    format: str = "json",
  ) -> None:
    """データエクスポートを記録"""
    self.log(
      action=AuditAction.DATA_EXPORT,
      resource_type=AuditResourceType.SYSTEM,
      user_id=user_id,
      ip_address=ip_address,
      details={"record_count": record_count, "format": format},
      status="success",
    )


# シングルトンインスタンス
_audit_service_instance: Optional[AuditService] = None


def get_audit_service() -> AuditService:
  """
  監査サービスのシングルトンインスタンスを取得

  Returns:
      AuditService: 監査サービスインスタンス
  """
  global _audit_service_instance
  if _audit_service_instance is None:
    _audit_service_instance = AuditService()
  return _audit_service_instance
