"""
Recipe Sharing Service Tests
レシピ共有サービスのテスト
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from backend.services.recipe_sharing_service import (
  RecipeSharingService,
  SharePermission,
  RecipeShare
)


@pytest.fixture
def temp_data_dir():
  """一時データディレクトリを作成"""
  temp_dir = tempfile.mkdtemp()
  yield temp_dir
  shutil.rmtree(temp_dir)


@pytest.fixture
def sharing_service(temp_data_dir):
  """RecipeSharingServiceインスタンスを作成"""
  return RecipeSharingService(data_dir=temp_data_dir)


class TestRecipeSharingService:
  """RecipeSharingServiceのテストクラス"""

  def test_initialization(self, temp_data_dir):
    """サービス初期化テスト"""
    service = RecipeSharingService(data_dir=temp_data_dir)
    assert service.data_dir.exists()
    assert service.shares_file.exists()
    assert service.history_file.exists()

  def test_create_share_link_basic(self, sharing_service):
    """基本的な共有リンク作成テスト"""
    share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001",
      permission=SharePermission.VIEW_ONLY,
      expires_in_days=7
    )

    assert share.share_id is not None
    assert share.recipe_id == "recipe_001"
    assert share.owner_id == "user_001"
    assert share.permission == SharePermission.VIEW_ONLY
    assert share.is_active is True
    assert share.access_count == 0
    assert share.share_link == f"/shared/{share.share_id}"
    assert share.expires_at is not None

  def test_create_share_link_with_shared_with(self, sharing_service):
    """共有相手を指定した共有リンク作成テスト"""
    shared_with = ["user@example.com", "user_002"]
    share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001",
      shared_with=shared_with
    )

    assert share.shared_with == shared_with

  def test_create_share_link_no_expiration(self, sharing_service):
    """無期限の共有リンク作成テスト"""
    share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001",
      expires_in_days=0
    )

    assert share.expires_at is None

  def test_create_share_link_edit_permission(self, sharing_service):
    """編集権限付き共有リンク作成テスト"""
    share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001",
      permission=SharePermission.EDIT
    )

    assert share.permission == SharePermission.EDIT

  def test_get_share_by_id_success(self, sharing_service):
    """共有ID取得成功テスト"""
    created_share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001"
    )

    retrieved_share = sharing_service.get_share_by_id(created_share.share_id)

    assert retrieved_share is not None
    assert retrieved_share.share_id == created_share.share_id
    assert retrieved_share.recipe_id == created_share.recipe_id
    assert retrieved_share.access_count == 1  # アクセスカウントが増加

  def test_get_share_by_id_not_found(self, sharing_service):
    """共有ID取得失敗テスト"""
    share = sharing_service.get_share_by_id("nonexistent_id")
    assert share is None

  def test_get_share_by_id_expired(self, sharing_service, temp_data_dir):
    """期限切れ共有取得テスト"""
    # 過去の有効期限で共有を作成
    share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001",
      expires_in_days=1
    )

    # 手動で有効期限を過去に設定
    shares = sharing_service._load_shares()
    for s in shares:
      if s["share_id"] == share.share_id:
        s["expires_at"] = (datetime.now() - timedelta(days=1)).isoformat()
    sharing_service._save_shares(shares)

    # 取得試行
    retrieved_share = sharing_service.get_share_by_id(share.share_id)
    assert retrieved_share is None

    # is_activeがFalseになっていることを確認
    shares = sharing_service._load_shares()
    for s in shares:
      if s["share_id"] == share.share_id:
        assert s["is_active"] is False

  def test_get_shares_by_recipe(self, sharing_service):
    """レシピIDによる共有リスト取得テスト"""
    recipe_id = "recipe_001"

    # 複数の共有を作成
    sharing_service.create_share_link(recipe_id=recipe_id, owner_id="user_001")
    sharing_service.create_share_link(recipe_id=recipe_id, owner_id="user_002")
    sharing_service.create_share_link(recipe_id="recipe_002", owner_id="user_001")

    shares = sharing_service.get_shares_by_recipe(recipe_id)

    assert len(shares) == 2
    for share in shares:
      assert share.recipe_id == recipe_id

  def test_get_shares_by_owner(self, sharing_service):
    """オーナーIDによる共有リスト取得テスト"""
    owner_id = "user_001"

    # 複数の共有を作成
    sharing_service.create_share_link(recipe_id="recipe_001", owner_id=owner_id)
    sharing_service.create_share_link(recipe_id="recipe_002", owner_id=owner_id)
    sharing_service.create_share_link(recipe_id="recipe_003", owner_id="user_002")

    shares = sharing_service.get_shares_by_owner(owner_id)

    assert len(shares) == 2
    for share in shares:
      assert share.owner_id == owner_id

  def test_get_shares_with_user(self, sharing_service):
    """ユーザーに共有されたレシピ取得テスト"""
    user_id = "user@example.com"

    # ユーザーを含む共有を作成
    sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001",
      shared_with=[user_id, "other@example.com"]
    )
    sharing_service.create_share_link(
      recipe_id="recipe_002",
      owner_id="user_002",
      shared_with=["other@example.com"]
    )

    shares = sharing_service.get_shares_with_user(user_id)

    assert len(shares) == 1
    assert shares[0].recipe_id == "recipe_001"

  def test_update_share_permission(self, sharing_service):
    """共有権限更新テスト"""
    share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001",
      permission=SharePermission.VIEW_ONLY
    )

    updated_share = sharing_service.update_share(
      share_id=share.share_id,
      permission=SharePermission.EDIT
    )

    assert updated_share is not None
    assert updated_share.permission == SharePermission.EDIT

  def test_update_share_expiration(self, sharing_service):
    """共有有効期限更新テスト"""
    share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001",
      expires_in_days=7
    )

    updated_share = sharing_service.update_share(
      share_id=share.share_id,
      expires_in_days=30
    )

    assert updated_share is not None
    # 有効期限が更新されていることを確認（正確な日時は比較しない）
    assert updated_share.expires_at is not None

  def test_update_share_shared_with(self, sharing_service):
    """共有相手更新テスト"""
    share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001",
      shared_with=["user@example.com"]
    )

    new_shared_with = ["user@example.com", "new@example.com"]
    updated_share = sharing_service.update_share(
      share_id=share.share_id,
      shared_with=new_shared_with
    )

    assert updated_share is not None
    assert updated_share.shared_with == new_shared_with

  def test_update_share_not_found(self, sharing_service):
    """存在しない共有の更新テスト"""
    updated_share = sharing_service.update_share(
      share_id="nonexistent_id",
      permission=SharePermission.EDIT
    )

    assert updated_share is None

  def test_revoke_share_success(self, sharing_service):
    """共有解除成功テスト"""
    share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001"
    )

    success = sharing_service.revoke_share(
      share_id=share.share_id,
      user_id="user_001"
    )

    assert success is True

    # 共有が無効化されていることを確認
    shares = sharing_service._load_shares()
    for s in shares:
      if s["share_id"] == share.share_id:
        assert s["is_active"] is False

  def test_revoke_share_unauthorized(self, sharing_service):
    """権限のない共有解除テスト"""
    share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001"
    )

    success = sharing_service.revoke_share(
      share_id=share.share_id,
      user_id="user_002"  # 別のユーザー
    )

    assert success is False

  def test_get_share_history(self, sharing_service):
    """共有履歴取得テスト"""
    share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001"
    )

    # 更新を実行
    sharing_service.update_share(
      share_id=share.share_id,
      permission=SharePermission.EDIT
    )

    # 解除を実行
    sharing_service.revoke_share(
      share_id=share.share_id,
      user_id="user_001"
    )

    history = sharing_service.get_share_history(share.share_id)

    assert len(history) >= 3  # created, updated, revoked
    actions = [entry["action"] for entry in history]
    assert "created" in actions
    assert "updated" in actions
    assert "revoked" in actions

  def test_cleanup_expired_shares(self, sharing_service):
    """期限切れ共有クリーンアップテスト"""
    # 通常の共有
    sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001",
      expires_in_days=7
    )

    # 期限切れ共有（手動で作成）
    expired_share = sharing_service.create_share_link(
      recipe_id="recipe_002",
      owner_id="user_001",
      expires_in_days=1
    )

    # 手動で有効期限を過去に設定
    shares = sharing_service._load_shares()
    for s in shares:
      if s["share_id"] == expired_share.share_id:
        s["expires_at"] = (datetime.now() - timedelta(days=1)).isoformat()
    sharing_service._save_shares(shares)

    # クリーンアップ実行
    count = sharing_service.cleanup_expired_shares()

    assert count == 1

  def test_get_share_stats(self, sharing_service):
    """共有統計取得テスト"""
    owner_id = "user_001"

    # 複数の共有を作成
    sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id=owner_id,
      permission=SharePermission.VIEW_ONLY
    )
    share2 = sharing_service.create_share_link(
      recipe_id="recipe_002",
      owner_id=owner_id,
      permission=SharePermission.EDIT
    )

    # アクセス
    sharing_service.get_share_by_id(share2.share_id)

    stats = sharing_service.get_share_stats(owner_id)

    assert stats["total_shares"] == 2
    assert stats["active_shares"] == 2
    assert stats["total_accesses"] >= 1
    assert stats["view_only_shares"] == 1
    assert stats["edit_shares"] == 1

  def test_access_count_increment(self, sharing_service):
    """アクセスカウント増加テスト"""
    share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001"
    )

    # 初期アクセスカウント
    assert share.access_count == 0

    # 複数回アクセス
    for i in range(3):
      retrieved_share = sharing_service.get_share_by_id(share.share_id)
      assert retrieved_share.access_count == i + 1

  def test_last_accessed_update(self, sharing_service):
    """最終アクセス日時更新テスト"""
    share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001"
    )

    # 初期状態
    assert share.last_accessed is None

    # アクセス
    retrieved_share = sharing_service.get_share_by_id(share.share_id)
    assert retrieved_share.last_accessed is not None

  def test_persistence(self, sharing_service, temp_data_dir):
    """永続化テスト"""
    share = sharing_service.create_share_link(
      recipe_id="recipe_001",
      owner_id="user_001"
    )

    # 新しいサービスインスタンスを作成
    new_service = RecipeSharingService(data_dir=temp_data_dir)

    # データが保持されていることを確認
    retrieved_share = new_service.get_share_by_id(share.share_id)
    assert retrieved_share is not None
    assert retrieved_share.recipe_id == share.recipe_id


if __name__ == "__main__":
  pytest.main([__file__, "-v"])
