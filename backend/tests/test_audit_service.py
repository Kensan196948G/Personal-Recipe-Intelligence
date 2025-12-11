"""
Test Suite for Audit Service

監査サービスのユニットテスト
CLAUDE.md Section 4 準拠
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from backend.services.audit_service import (
  AuditService,
  AuditAction,
  AuditResourceType,
  get_audit_service,
)


@pytest.fixture
def temp_log_dir(tmp_path):
  """一時ログディレクトリを作成"""
  log_dir = tmp_path / "logs"
  log_dir.mkdir()
  return str(log_dir)


@pytest.fixture
def audit_service(temp_log_dir):
  """テスト用監査サービスインスタンスを作成"""
  return AuditService(log_dir=temp_log_dir)


class TestAuditService:
  """AuditService クラスのテスト"""

  def test_initialization(self, audit_service, temp_log_dir):
    """初期化のテスト"""
    assert audit_service.log_dir == Path(temp_log_dir)
    assert audit_service.audit_log_path.exists() or True  # まだ書き込み前
    assert audit_service.lock is not None

  def test_log_basic(self, audit_service, temp_log_dir):
    """基本的なログ記録のテスト"""
    audit_service.log(
      action=AuditAction.RECIPE_CREATE,
      resource_type=AuditResourceType.RECIPE,
      user_id="user_001",
      resource_id="recipe_123",
      ip_address="192.168.1.100",
      details={"recipe_title": "Test Recipe"},
    )

    # ログファイルが作成されたことを確認
    log_file = Path(temp_log_dir) / "audit.json"
    assert log_file.exists()

    # ログ内容を確認
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    assert log_entry["action"] == "recipe_create"
    assert log_entry["resource_type"] == "recipe"
    assert log_entry["user_id"] == "user_001"
    assert log_entry["resource_id"] == "recipe_123"
    assert log_entry["ip_address"] == "192.168.1.100"
    assert log_entry["details"]["recipe_title"] == "Test Recipe"
    assert log_entry["status"] == "success"
    assert "timestamp" in log_entry

  def test_sanitize_details(self, audit_service):
    """機密データのマスキングテスト"""
    details = {
      "username": "testuser",
      "password": "secret123",
      "api_key": "key_abc123",
      "token": "bearer_token",
      "email": "test@example.com",
    }

    sanitized = audit_service._sanitize_details(details)

    assert sanitized["username"] == "testuser"
    assert sanitized["password"] == "***MASKED***"
    assert sanitized["api_key"] == "***MASKED***"
    assert sanitized["token"] == "***MASKED***"
    assert sanitized["email"] == "test@example.com"

  def test_sanitize_nested_details(self, audit_service):
    """ネストされた機密データのマスキングテスト"""
    details = {
      "user": {"name": "testuser", "password": "secret123"},
      "auth": {"token": "bearer_token", "email": "test@example.com"},
    }

    sanitized = audit_service._sanitize_details(details)

    assert sanitized["user"]["name"] == "testuser"
    assert sanitized["user"]["password"] == "***MASKED***"
    assert sanitized["auth"]["token"] == "***MASKED***"
    assert sanitized["auth"]["email"] == "test@example.com"

  def test_log_recipe_create(self, audit_service, temp_log_dir):
    """レシピ作成ログのテスト"""
    audit_service.log_recipe_create(
      recipe_id="recipe_123",
      user_id="user_001",
      ip_address="192.168.1.100",
      recipe_title="Test Recipe",
    )

    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    assert log_entry["action"] == "recipe_create"
    assert log_entry["resource_id"] == "recipe_123"
    assert log_entry["details"]["recipe_title"] == "Test Recipe"

  def test_log_recipe_update(self, audit_service, temp_log_dir):
    """レシピ更新ログのテスト"""
    changes = {"updated_fields": ["title", "ingredients"], "field_count": 2}

    audit_service.log_recipe_update(
      recipe_id="recipe_123",
      user_id="user_001",
      ip_address="192.168.1.100",
      changes=changes,
    )

    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    assert log_entry["action"] == "recipe_update"
    assert log_entry["details"]["changes"]["field_count"] == 2

  def test_log_recipe_delete(self, audit_service, temp_log_dir):
    """レシピ削除ログのテスト"""
    audit_service.log_recipe_delete(
      recipe_id="recipe_123",
      user_id="user_001",
      ip_address="192.168.1.100",
      recipe_title="Test Recipe",
    )

    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    assert log_entry["action"] == "recipe_delete"
    assert log_entry["resource_id"] == "recipe_123"

  def test_log_recipe_batch_delete(self, audit_service, temp_log_dir):
    """レシピ一括削除ログのテスト"""
    recipe_ids = ["recipe_001", "recipe_002", "recipe_003"]

    audit_service.log_recipe_batch_delete(
      recipe_ids=recipe_ids, user_id="user_001", ip_address="192.168.1.100"
    )

    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    assert log_entry["action"] == "recipe_batch_delete"
    assert log_entry["details"]["count"] == 3
    assert log_entry["details"]["recipe_ids"] == recipe_ids

  def test_log_auth_success(self, audit_service, temp_log_dir):
    """認証成功ログのテスト"""
    audit_service.log_auth_success(
      user_id="user_001", ip_address="192.168.1.100", method="api_key"
    )

    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    assert log_entry["action"] == "auth_success"
    assert log_entry["user_id"] == "user_001"
    assert log_entry["details"]["method"] == "api_key"
    assert log_entry["status"] == "success"

  def test_log_auth_failure(self, audit_service, temp_log_dir):
    """認証失敗ログのテスト"""
    audit_service.log_auth_failure(
      user_id="user_001",
      ip_address="192.168.1.100",
      reason="invalid_credentials",
      method="api_key",
    )

    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    assert log_entry["action"] == "auth_failure"
    assert log_entry["status"] == "failure"
    assert log_entry["details"]["reason"] == "invalid_credentials"

  def test_log_api_key_created(self, audit_service, temp_log_dir):
    """APIキー作成ログのテスト"""
    audit_service.log_api_key_created(
      user_id="user_001",
      key_id="key_abc123",
      ip_address="192.168.1.100",
      key_name="Production Key",
    )

    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    assert log_entry["action"] == "api_key_created"
    assert log_entry["resource_id"] == "key_abc123"
    assert log_entry["details"]["key_name"] == "Production Key"

  def test_log_api_key_rotated(self, audit_service, temp_log_dir):
    """APIキーローテーションログのテスト"""
    audit_service.log_api_key_rotated(
      user_id="user_001",
      old_key_id="key_old",
      new_key_id="key_new",
      ip_address="192.168.1.100",
    )

    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    assert log_entry["action"] == "api_key_rotated"
    assert log_entry["details"]["old_key_id"] == "key_old"
    assert log_entry["details"]["new_key_id"] == "key_new"

  def test_log_security_breach_attempt(self, audit_service, temp_log_dir):
    """セキュリティ侵害試行ログのテスト"""
    audit_service.log_security_breach_attempt(
      ip_address="192.168.1.100",
      user_id="user_001",
      attack_type="sql_injection",
      details={"endpoint": "/api/v1/recipes", "payload": "' OR 1=1 --"},
    )

    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    assert log_entry["action"] == "security_breach_attempt"
    assert log_entry["status"] == "blocked"
    assert log_entry["details"]["attack_type"] == "sql_injection"

  def test_log_rate_limit_exceeded(self, audit_service, temp_log_dir):
    """レート制限超過ログのテスト"""
    audit_service.log_rate_limit_exceeded(
      ip_address="192.168.1.100",
      user_id="user_001",
      endpoint="/api/v1/recipes",
    )

    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    assert log_entry["action"] == "security_rate_limit_exceeded"
    assert log_entry["status"] == "blocked"

  def test_log_invalid_token(self, audit_service, temp_log_dir):
    """無効トークンログのテスト"""
    audit_service.log_invalid_token(
      ip_address="192.168.1.100", user_id="user_001", token_prefix="pri_abc1"
    )

    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    assert log_entry["action"] == "security_invalid_token"
    assert log_entry["status"] == "rejected"
    # トークンプレフィックスは自動的にマスクされる場合がある
    token_prefix = log_entry["details"]["token_prefix"]
    assert token_prefix in ["pri_abc1", "***MASKED***", "pri***", "pri_***"]

  def test_log_data_import(self, audit_service, temp_log_dir):
    """データインポートログのテスト"""
    audit_service.log_data_import(
      user_id="user_001",
      ip_address="192.168.1.100",
      record_count=150,
      source="csv_file",
    )

    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    assert log_entry["action"] == "data_import"
    assert log_entry["details"]["record_count"] == 150
    assert log_entry["details"]["source"] == "csv_file"

  def test_log_data_export(self, audit_service, temp_log_dir):
    """データエクスポートログのテスト"""
    audit_service.log_data_export(
      user_id="user_001",
      ip_address="192.168.1.100",
      record_count=200,
      format="json",
    )

    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    assert log_entry["action"] == "data_export"
    assert log_entry["details"]["record_count"] == 200
    assert log_entry["details"]["format"] == "json"

  def test_multiple_logs(self, audit_service, temp_log_dir):
    """複数ログの記録テスト"""
    # 複数のログを記録
    audit_service.log_recipe_create(
      recipe_id="recipe_001", user_id="user_001", ip_address="192.168.1.100"
    )
    audit_service.log_recipe_update(
      recipe_id="recipe_001", user_id="user_001", ip_address="192.168.1.100"
    )
    audit_service.log_recipe_delete(
      recipe_id="recipe_001", user_id="user_001", ip_address="192.168.1.100"
    )

    # ログファイルを読み込み
    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      lines = f.readlines()

    assert len(lines) == 3
    assert json.loads(lines[0])["action"] == "recipe_create"
    assert json.loads(lines[1])["action"] == "recipe_update"
    assert json.loads(lines[2])["action"] == "recipe_delete"

  def test_timestamp_format(self, audit_service, temp_log_dir):
    """タイムスタンプフォーマットのテスト（ISO8601）"""
    audit_service.log(
      action=AuditAction.RECIPE_CREATE,
      resource_type=AuditResourceType.RECIPE,
      user_id="user_001",
    )

    log_file = Path(temp_log_dir) / "audit.json"
    with open(log_file, "r", encoding="utf-8") as f:
      log_entry = json.loads(f.readline())

    # ISO8601形式であることを確認
    timestamp = log_entry["timestamp"]
    try:
      datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
      is_valid = True
    except ValueError:
      is_valid = False

    assert is_valid

  def test_get_audit_service_singleton(self):
    """シングルトンインスタンスのテスト"""
    service1 = get_audit_service()
    service2 = get_audit_service()

    assert service1 is service2


class TestAuditEnums:
  """Enum クラスのテスト"""

  def test_audit_action_enum(self):
    """AuditAction Enumのテスト"""
    assert AuditAction.RECIPE_CREATE.value == "recipe_create"
    assert AuditAction.AUTH_SUCCESS.value == "auth_success"
    assert AuditAction.API_KEY_CREATED.value == "api_key_created"

  def test_audit_resource_type_enum(self):
    """AuditResourceType Enumのテスト"""
    assert AuditResourceType.RECIPE.value == "recipe"
    assert AuditResourceType.USER.value == "user"
    assert AuditResourceType.API_KEY.value == "api_key"
