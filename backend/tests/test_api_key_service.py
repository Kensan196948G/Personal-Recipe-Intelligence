"""
Tests for API Key Service

APIキーサービスのテスト
"""

import pytest
import tempfile
import shutil
import time

from backend.services.api_key_service import (
  APIKeyService,
  APIKeyScope,
  RateLimit,
  UsageRecord
)


@pytest.fixture
def temp_dir():
  """一時ディレクトリを作成"""
  temp = tempfile.mkdtemp()
  yield temp
  shutil.rmtree(temp)


@pytest.fixture
def service(temp_dir):
  """APIキーサービスのインスタンスを作成"""
  return APIKeyService(data_dir=temp_dir)


class TestAPIKeyGeneration:
  """APIキー生成のテスト"""

  def test_generate_api_key_default(self, service):
    """デフォルト設定でAPIキーを生成"""
    raw_key, api_key = service.generate_api_key(name="Test Key")

    # キーが生成されていることを確認
    assert raw_key is not None
    assert len(raw_key) > 0
    assert api_key.key_id is not None
    assert api_key.name == "Test Key"
    assert api_key.is_active is True

    # デフォルトスコープを確認
    assert api_key.scope.read_recipes is True
    assert api_key.scope.write_recipes is False
    assert api_key.scope.delete_recipes is False

    # デフォルトレート制限を確認
    assert api_key.rate_limit.requests_per_minute == 60
    assert api_key.rate_limit.requests_per_hour == 1000
    assert api_key.rate_limit.requests_per_day == 10000

  def test_generate_api_key_custom_scope(self, service):
    """カスタムスコープでAPIキーを生成"""
    scope = APIKeyScope(
      read_recipes=True,
      write_recipes=True,
      delete_recipes=True,
      read_tags=True,
      write_tags=True
    )

    raw_key, api_key = service.generate_api_key(
      name="Full Access Key",
      scope=scope
    )

    assert api_key.scope.read_recipes is True
    assert api_key.scope.write_recipes is True
    assert api_key.scope.delete_recipes is True
    assert api_key.scope.read_tags is True
    assert api_key.scope.write_tags is True

  def test_generate_api_key_custom_rate_limit(self, service):
    """カスタムレート制限でAPIキーを生成"""
    rate_limit = RateLimit(
      requests_per_minute=120,
      requests_per_hour=5000,
      requests_per_day=50000
    )

    raw_key, api_key = service.generate_api_key(
      name="High Limit Key",
      rate_limit=rate_limit
    )

    assert api_key.rate_limit.requests_per_minute == 120
    assert api_key.rate_limit.requests_per_hour == 5000
    assert api_key.rate_limit.requests_per_day == 50000

  def test_generate_multiple_keys(self, service):
    """複数のAPIキーを生成"""
    key1_raw, key1 = service.generate_api_key(name="Key 1")
    key2_raw, key2 = service.generate_api_key(name="Key 2")

    # キーが異なることを確認
    assert key1_raw != key2_raw
    assert key1.key_id != key2.key_id
    assert key1.key_hash != key2.key_hash

    # 両方のキーがサービスに登録されていることを確認
    assert len(service.keys) == 2


class TestAPIKeyVerification:
  """APIキー検証のテスト"""

  def test_verify_valid_key(self, service):
    """有効なキーを検証"""
    raw_key, api_key = service.generate_api_key(name="Test Key")

    verified = service.verify_api_key(raw_key)

    assert verified is not None
    assert verified.key_id == api_key.key_id
    assert verified.name == api_key.name

  def test_verify_invalid_key(self, service):
    """無効なキーを検証"""
    verified = service.verify_api_key("invalid_key")

    assert verified is None

  def test_verify_revoked_key(self, service):
    """無効化されたキーを検証"""
    raw_key, api_key = service.generate_api_key(name="Test Key")

    # キーを無効化
    service.revoke_api_key(api_key.key_id)

    # 検証は失敗する
    verified = service.verify_api_key(raw_key)
    assert verified is None


class TestAPIKeyManagement:
  """APIキー管理のテスト"""

  def test_revoke_api_key(self, service):
    """APIキーを無効化"""
    raw_key, api_key = service.generate_api_key(name="Test Key")

    success = service.revoke_api_key(api_key.key_id)

    assert success is True
    assert service.keys[api_key.key_id].is_active is False

  def test_revoke_nonexistent_key(self, service):
    """存在しないキーを無効化"""
    success = service.revoke_api_key("nonexistent_id")

    assert success is False

  def test_delete_api_key(self, service):
    """APIキーを削除"""
    raw_key, api_key = service.generate_api_key(name="Test Key")

    success = service.delete_api_key(api_key.key_id)

    assert success is True
    assert api_key.key_id not in service.keys
    assert api_key.key_id not in service.usage

  def test_delete_nonexistent_key(self, service):
    """存在しないキーを削除"""
    success = service.delete_api_key("nonexistent_id")

    assert success is False

  def test_list_api_keys(self, service):
    """APIキー一覧を取得"""
    service.generate_api_key(name="Key 1")
    service.generate_api_key(name="Key 2")
    service.generate_api_key(name="Key 3")

    keys = service.list_api_keys()

    assert len(keys) == 3
    assert all("key_hash" not in k for k in keys)  # ハッシュは含まれない

  def test_rotate_api_key(self, service):
    """APIキーをローテーション"""
    raw_key, api_key = service.generate_api_key(name="Test Key")

    result = service.rotate_api_key(api_key.key_id)

    assert result is not None
    new_raw_key, new_api_key = result

    # 新しいキーが生成されている
    assert new_raw_key != raw_key
    assert new_api_key.key_id != api_key.key_id

    # 古いキーが無効化されている
    assert service.keys[api_key.key_id].is_active is False

    # 新しいキーは有効
    assert service.keys[new_api_key.key_id].is_active is True

  def test_rotate_nonexistent_key(self, service):
    """存在しないキーをローテーション"""
    result = service.rotate_api_key("nonexistent_id")

    assert result is None


class TestRateLimiting:
  """レート制限のテスト"""

  def test_rate_limit_within_limit(self, service):
    """制限内のリクエスト"""
    raw_key, api_key = service.generate_api_key(name="Test Key")

    # 1回目のチェック
    is_allowed, error = service.check_rate_limit(api_key.key_id)

    assert is_allowed is True
    assert error is None

  def test_rate_limit_per_minute(self, service):
    """分単位のレート制限"""
    rate_limit = RateLimit(requests_per_minute=5)
    raw_key, api_key = service.generate_api_key(
      name="Limited Key",
      rate_limit=rate_limit
    )

    # 5回リクエストを記録
    for i in range(5):
      service.record_usage(api_key.key_id, "/test", 200)

    # 6回目は制限に引っかかる
    is_allowed, error = service.check_rate_limit(api_key.key_id)

    assert is_allowed is False
    assert "per minute" in error

  def test_rate_limit_inactive_key(self, service):
    """無効化されたキーのレート制限チェック"""
    raw_key, api_key = service.generate_api_key(name="Test Key")
    service.revoke_api_key(api_key.key_id)

    is_allowed, error = service.check_rate_limit(api_key.key_id)

    assert is_allowed is False
    assert "inactive" in error

  def test_rate_limit_nonexistent_key(self, service):
    """存在しないキーのレート制限チェック"""
    is_allowed, error = service.check_rate_limit("nonexistent_id")

    assert is_allowed is False
    assert "Invalid" in error

  def test_rate_limit_cleanup_old_records(self, service):
    """古い記録のクリーンアップ"""
    rate_limit = RateLimit(requests_per_minute=5)
    raw_key, api_key = service.generate_api_key(
      name="Test Key",
      rate_limit=rate_limit
    )

    # 古いタイムスタンプで記録を追加
    old_time = time.time() - 90000  # 25時間前
    for i in range(5):
      record = UsageRecord(
        timestamp=old_time,
        endpoint="/test",
        status_code=200
      )
      service.usage[api_key.key_id].append(record)

    # チェック（古い記録はクリーンアップされる）
    is_allowed, error = service.check_rate_limit(api_key.key_id)

    assert is_allowed is True
    assert len(service.usage[api_key.key_id]) == 0


class TestUsageTracking:
  """使用量トラッキングのテスト"""

  def test_record_usage(self, service):
    """使用量を記録"""
    raw_key, api_key = service.generate_api_key(name="Test Key")

    service.record_usage(api_key.key_id, "/api/recipes", 200)

    assert len(service.usage[api_key.key_id]) == 1
    assert service.keys[api_key.key_id].usage_count == 1
    assert service.keys[api_key.key_id].last_used_at is not None

  def test_get_usage_stats(self, service):
    """使用量統計を取得"""
    rate_limit = RateLimit(
      requests_per_minute=60,
      requests_per_hour=1000,
      requests_per_day=10000
    )
    raw_key, api_key = service.generate_api_key(
      name="Test Key",
      rate_limit=rate_limit
    )

    # いくつかリクエストを記録
    for i in range(5):
      service.record_usage(api_key.key_id, "/api/recipes", 200)

    stats = service.get_usage_stats(api_key.key_id)

    assert stats is not None
    assert stats["key_id"] == api_key.key_id
    assert stats["total_requests"] == 5
    assert stats["current_usage"]["last_minute"] == 5
    assert stats["current_usage"]["last_hour"] == 5
    assert stats["current_usage"]["last_day"] == 5
    assert stats["remaining"]["per_minute"] == 55
    assert stats["remaining"]["per_hour"] == 995
    assert stats["remaining"]["per_day"] == 9995

  def test_get_usage_stats_nonexistent_key(self, service):
    """存在しないキーの使用量統計"""
    stats = service.get_usage_stats("nonexistent_id")

    assert stats is None


class TestScopeManagement:
  """スコープ管理のテスト"""

  def test_check_scope_read_recipes(self, service):
    """レシピ読み取りスコープをチェック"""
    scope = APIKeyScope(read_recipes=True, write_recipes=False)
    raw_key, api_key = service.generate_api_key(name="Test Key", scope=scope)

    has_scope = service.check_scope(api_key.key_id, "read_recipes")

    assert has_scope is True

  def test_check_scope_write_recipes(self, service):
    """レシピ書き込みスコープをチェック"""
    scope = APIKeyScope(read_recipes=True, write_recipes=False)
    raw_key, api_key = service.generate_api_key(name="Test Key", scope=scope)

    has_scope = service.check_scope(api_key.key_id, "write_recipes")

    assert has_scope is False

  def test_check_scope_nonexistent_key(self, service):
    """存在しないキーのスコープチェック"""
    has_scope = service.check_scope("nonexistent_id", "read_recipes")

    assert has_scope is False

  def test_check_scope_invalid_scope(self, service):
    """存在しないスコープをチェック"""
    raw_key, api_key = service.generate_api_key(name="Test Key")

    has_scope = service.check_scope(api_key.key_id, "invalid_scope")

    assert has_scope is False


class TestPersistence:
  """永続化のテスト"""

  def test_save_and_load_keys(self, temp_dir):
    """キーの保存と読み込み"""
    # 最初のサービスでキーを作成
    service1 = APIKeyService(data_dir=temp_dir)
    raw_key, api_key = service1.generate_api_key(name="Test Key")

    # 新しいサービスインスタンスで読み込み
    service2 = APIKeyService(data_dir=temp_dir)

    assert len(service2.keys) == 1
    assert api_key.key_id in service2.keys

    # キーを検証できることを確認
    verified = service2.verify_api_key(raw_key)
    assert verified is not None

  def test_save_and_load_usage(self, temp_dir):
    """使用量の保存と読み込み"""
    # 最初のサービスで使用量を記録
    service1 = APIKeyService(data_dir=temp_dir)
    raw_key, api_key = service1.generate_api_key(name="Test Key")
    service1.record_usage(api_key.key_id, "/test", 200)

    # 新しいサービスインスタンスで読み込み
    service2 = APIKeyService(data_dir=temp_dir)

    assert len(service2.usage[api_key.key_id]) == 1

  def test_multiple_save_load_cycles(self, temp_dir):
    """複数回の保存と読み込み"""
    service1 = APIKeyService(data_dir=temp_dir)
    raw_key1, key1 = service1.generate_api_key(name="Key 1")

    service2 = APIKeyService(data_dir=temp_dir)
    raw_key2, key2 = service2.generate_api_key(name="Key 2")

    service3 = APIKeyService(data_dir=temp_dir)

    assert len(service3.keys) == 2
    assert key1.key_id in service3.keys
    assert key2.key_id in service3.keys


if __name__ == "__main__":
  pytest.main([__file__, "-v"])
