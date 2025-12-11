"""
管理者サービスのテスト
"""

import json
import tempfile
from datetime import datetime, timedelta

import pytest

from backend.services.admin_service import AdminService


@pytest.fixture
def temp_data_dir():
  """一時データディレクトリ"""
  with tempfile.TemporaryDirectory() as tmpdir:
    yield tmpdir


@pytest.fixture
def admin_service(temp_data_dir):
  """AdminServiceインスタンス"""
  return AdminService(data_dir=temp_data_dir)


class TestAdminService:
  """AdminService のテスト"""

  def test_get_settings_default(self, admin_service):
    """デフォルト設定の取得"""
    settings = admin_service.get_settings()

    assert settings is not None
    assert "site_name" in settings
    assert "max_upload_size_mb" in settings
    assert "enable_public_recipes" in settings
    assert "enable_user_registration" in settings
    assert "default_language" in settings
    assert "timezone" in settings
    assert "pagination_size" in settings
    assert "cache_ttl_seconds" in settings
    assert "ocr_enabled" in settings
    assert "scraping_enabled" in settings
    assert "max_recipes_per_user" in settings
    assert "maintenance_mode" in settings

    # デフォルト値チェック
    assert settings["site_name"] == "Personal Recipe Intelligence"
    assert settings["default_language"] == "ja"
    assert settings["timezone"] == "Asia/Tokyo"
    assert settings["maintenance_mode"] is False

  def test_update_settings(self, admin_service):
    """設定の更新"""
    # 初期設定取得
    settings = admin_service.get_settings()

    # 設定更新
    new_settings = {
      "site_name": "Updated Site Name",
      "max_upload_size_mb": 50,
      "maintenance_mode": True,
    }
    updated = admin_service.update_settings(new_settings)

    # 更新確認
    assert updated["site_name"] == "Updated Site Name"
    assert updated["max_upload_size_mb"] == 50
    assert updated["maintenance_mode"] is True

    # 他の設定が保持されていることを確認
    assert updated["default_language"] == settings["default_language"]
    assert updated["timezone"] == settings["timezone"]

    # 再取得して永続化確認
    reloaded = admin_service.get_settings()
    assert reloaded["site_name"] == "Updated Site Name"
    assert reloaded["maintenance_mode"] is True

  def test_get_system_stats(self, admin_service):
    """システム統計の取得"""
    stats = admin_service.get_system_stats()

    assert stats is not None
    assert "timestamp" in stats
    assert "recipes" in stats
    assert "users" in stats
    assert "tags" in stats
    assert "system" in stats

  def test_get_recipe_stats(self, admin_service):
    """レシピ統計の取得"""
    stats = admin_service.get_recipe_stats(days=30)

    assert stats is not None
    assert "period_days" in stats
    assert stats["period_days"] == 30
    assert "total_recipes" in stats
    assert "daily_counts" in stats
    assert "source_counts" in stats
    assert "averages" in stats

  def test_get_recipe_stats_with_period(self, admin_service):
    """期間指定でのレシピ統計取得"""
    # 7日間
    stats_7d = admin_service.get_recipe_stats(days=7)
    assert stats_7d["period_days"] == 7

    # 90日間
    stats_90d = admin_service.get_recipe_stats(days=90)
    assert stats_90d["period_days"] == 90

  def test_get_user_stats(self, admin_service):
    """ユーザー統計の取得"""
    stats = admin_service.get_user_stats(days=30)

    assert stats is not None
    assert "period_days" in stats
    assert stats["period_days"] == 30
    assert "new_users" in stats
    assert "active_users" in stats
    assert "daily_logins" in stats
    assert "top_contributors" in stats

  def test_get_health_check(self, admin_service):
    """ヘルスチェックの実行"""
    health = admin_service.get_health_check()

    assert health is not None
    assert "status" in health
    assert health["status"] in ["healthy", "degraded", "unhealthy"]
    assert "timestamp" in health
    assert "checks" in health

    # 各チェック項目の確認
    checks = health["checks"]
    assert "database" in checks
    assert "disk" in checks
    assert "data_directory" in checks

  def test_stats_cache(self, admin_service):
    """統計キャッシュの動作確認"""
    # 初回取得（キャッシュなし）
    stats1 = admin_service.get_system_stats()
    assert stats1 is not None

    # キャッシュファイルが作成されたことを確認
    assert admin_service.stats_cache_file.exists()

    # 2回目取得（キャッシュから）
    stats2 = admin_service.get_system_stats()
    assert stats2 is not None
    assert stats1["timestamp"] == stats2["timestamp"]

    # キャッシュクリア
    admin_service.clear_stats_cache()
    assert not admin_service.stats_cache_file.exists()

  def test_settings_persistence(self, admin_service, temp_data_dir):
    """設定の永続化テスト"""
    # 設定更新
    settings1 = {"site_name": "Test Site", "maintenance_mode": True}
    admin_service.update_settings(settings1)

    # 新しいインスタンスで設定取得
    admin_service2 = AdminService(data_dir=temp_data_dir)
    settings2 = admin_service2.get_settings()

    assert settings2["site_name"] == "Test Site"
    assert settings2["maintenance_mode"] is True

  def test_logs_without_logs_directory(self, admin_service):
    """ログディレクトリがない場合"""
    logs = admin_service.get_system_logs()
    assert logs == []

  def test_cache_expiration(self, admin_service):
    """キャッシュの有効期限テスト"""
    # 統計取得（キャッシュ作成）
    stats1 = admin_service.get_system_stats()

    # キャッシュファイルの更新日時を古くする
    cache_data = {
      **stats1,
      "timestamp": (datetime.utcnow() - timedelta(seconds=400)).isoformat(),
    }
    with open(admin_service.stats_cache_file, "w", encoding="utf-8") as f:
      json.dump(cache_data, f)

    # 再取得（キャッシュ期限切れで新規取得）
    stats2 = admin_service.get_system_stats()
    assert stats2["timestamp"] != cache_data["timestamp"]

  def test_database_size_calculation(self, admin_service):
    """データベースサイズの計算"""
    size_str = admin_service._get_database_size()
    assert "MB" in size_str or "unknown" in size_str

  def test_storage_used_calculation(self, admin_service):
    """ストレージ使用量の計算"""
    size_str = admin_service._get_storage_used()
    assert "MB" in size_str or "unknown" in size_str
