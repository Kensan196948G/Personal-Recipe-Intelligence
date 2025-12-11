"""
Follow Service のテスト
"""

import pytest
import tempfile
import shutil
from backend.services.follow_service import FollowService


@pytest.fixture
def temp_data_dir():
  """一時データディレクトリを作成"""
  temp_dir = tempfile.mkdtemp()
  yield temp_dir
  shutil.rmtree(temp_dir)


@pytest.fixture
def follow_service(temp_data_dir):
  """フォローサービスのインスタンスを作成"""
  service = FollowService(data_dir=temp_data_dir)

  # テストユーザーを作成
  users = [
    {
      "id": "user_1",
      "username": "alice",
      "display_name": "Alice",
      "bio": "料理好き",
      "avatar_url": None,
    },
    {
      "id": "user_2",
      "username": "bob",
      "display_name": "Bob",
      "bio": "パン職人",
      "avatar_url": None,
    },
    {
      "id": "user_3",
      "username": "charlie",
      "display_name": "Charlie",
      "bio": "デザート専門",
      "avatar_url": None,
    },
    {
      "id": "user_4",
      "username": "diana",
      "display_name": "Diana",
      "bio": "和食マスター",
      "avatar_url": None,
    },
  ]
  service._save_users(users)

  # テストレシピを作成
  recipes = [
    {
      "id": "recipe_1",
      "user_id": "user_2",
      "title": "フランスパン",
      "created_at": "2025-12-10T10:00:00",
    },
    {
      "id": "recipe_2",
      "user_id": "user_2",
      "title": "クロワッサン",
      "created_at": "2025-12-10T12:00:00",
    },
    {
      "id": "recipe_3",
      "user_id": "user_3",
      "title": "チョコレートケーキ",
      "created_at": "2025-12-10T14:00:00",
    },
  ]
  service._save_recipes(recipes)

  return service


class TestFollowUser:
  """フォロー機能のテスト"""

  def test_follow_user_success(self, follow_service):
    """正常にフォローできる"""
    result = follow_service.follow_user("user_1", "user_2")

    assert result["follower_id"] == "user_1"
    assert result["following_id"] == "user_2"
    assert "created_at" in result
    assert "id" in result

  def test_follow_user_duplicate(self, follow_service):
    """重複フォローは既存のデータを返す"""
    result1 = follow_service.follow_user("user_1", "user_2")
    result2 = follow_service.follow_user("user_1", "user_2")

    assert result1["id"] == result2["id"]

  def test_follow_self_error(self, follow_service):
    """自分自身をフォローできない"""
    with pytest.raises(ValueError, match="自分自身をフォロー"):
      follow_service.follow_user("user_1", "user_1")

  def test_follow_nonexistent_user_error(self, follow_service):
    """存在しないユーザーをフォローできない"""
    with pytest.raises(ValueError, match="が存在しません"):
      follow_service.follow_user("user_1", "user_999")

  def test_follow_by_nonexistent_user_error(self, follow_service):
    """存在しないユーザーがフォローできない"""
    with pytest.raises(ValueError, match="が存在しません"):
      follow_service.follow_user("user_999", "user_2")


class TestUnfollowUser:
  """アンフォロー機能のテスト"""

  def test_unfollow_success(self, follow_service):
    """正常にアンフォローできる"""
    follow_service.follow_user("user_1", "user_2")
    result = follow_service.unfollow_user("user_1", "user_2")

    assert result is True
    assert not follow_service.is_following("user_1", "user_2")

  def test_unfollow_nonexistent_follow(self, follow_service):
    """存在しないフォロー関係をアンフォローするとFalse"""
    result = follow_service.unfollow_user("user_1", "user_2")
    assert result is False


class TestGetFollowers:
  """フォロワー取得のテスト"""

  def test_get_followers_success(self, follow_service):
    """フォロワー一覧を取得できる"""
    follow_service.follow_user("user_1", "user_2")
    follow_service.follow_user("user_3", "user_2")

    result = follow_service.get_followers("user_2")

    assert result["total"] == 2
    assert len(result["followers"]) == 2
    follower_ids = [f["id"] for f in result["followers"]]
    assert "user_1" in follower_ids
    assert "user_3" in follower_ids

  def test_get_followers_empty(self, follow_service):
    """フォロワーがいない場合は空リスト"""
    result = follow_service.get_followers("user_1")

    assert result["total"] == 0
    assert result["followers"] == []

  def test_get_followers_with_pagination(self, follow_service):
    """ページネーションが機能する"""
    follow_service.follow_user("user_1", "user_2")
    follow_service.follow_user("user_3", "user_2")
    follow_service.follow_user("user_4", "user_2")

    result = follow_service.get_followers("user_2", limit=2, offset=0)
    assert len(result["followers"]) == 2
    assert result["total"] == 3

    result = follow_service.get_followers("user_2", limit=2, offset=2)
    assert len(result["followers"]) == 1

  def test_get_followers_mutual_info(self, follow_service):
    """相互フォロー情報が含まれる"""
    follow_service.follow_user("user_1", "user_2")
    follow_service.follow_user("user_2", "user_1")

    result = follow_service.get_followers("user_2")
    follower = result["followers"][0]

    assert follower["is_mutual"] is True
    assert follower["is_following"] is True


class TestGetFollowing:
  """フォロー中取得のテスト"""

  def test_get_following_success(self, follow_service):
    """フォロー中ユーザー一覧を取得できる"""
    follow_service.follow_user("user_1", "user_2")
    follow_service.follow_user("user_1", "user_3")

    result = follow_service.get_following("user_1")

    assert result["total"] == 2
    assert len(result["following"]) == 2
    following_ids = [f["id"] for f in result["following"]]
    assert "user_2" in following_ids
    assert "user_3" in following_ids

  def test_get_following_empty(self, follow_service):
    """フォロー中ユーザーがいない場合は空リスト"""
    result = follow_service.get_following("user_1")

    assert result["total"] == 0
    assert result["following"] == []


class TestIsFollowing:
  """フォロー関係チェックのテスト"""

  def test_is_following_true(self, follow_service):
    """フォロー中の場合True"""
    follow_service.follow_user("user_1", "user_2")
    assert follow_service.is_following("user_1", "user_2") is True

  def test_is_following_false(self, follow_service):
    """フォローしていない場合False"""
    assert follow_service.is_following("user_1", "user_2") is False


class TestIsMutualFollow:
  """相互フォロー判定のテスト"""

  def test_is_mutual_follow_true(self, follow_service):
    """相互フォローの場合True"""
    follow_service.follow_user("user_1", "user_2")
    follow_service.follow_user("user_2", "user_1")
    assert follow_service.is_mutual_follow("user_1", "user_2") is True

  def test_is_mutual_follow_false(self, follow_service):
    """相互フォローでない場合False"""
    follow_service.follow_user("user_1", "user_2")
    assert follow_service.is_mutual_follow("user_1", "user_2") is False


class TestGetFollowStatus:
  """フォロー状態取得のテスト"""

  def test_get_follow_status_following(self, follow_service):
    """フォロー中の状態を取得"""
    follow_service.follow_user("user_1", "user_2")

    status = follow_service.get_follow_status("user_1", "user_2")

    assert status["is_following"] is True
    assert status["is_follower"] is False
    assert status["is_mutual"] is False
    assert status["follower_count"] == 1
    assert status["following_count"] == 0

  def test_get_follow_status_mutual(self, follow_service):
    """相互フォローの状態を取得"""
    follow_service.follow_user("user_1", "user_2")
    follow_service.follow_user("user_2", "user_1")

    status = follow_service.get_follow_status("user_1", "user_2")

    assert status["is_following"] is True
    assert status["is_follower"] is True
    assert status["is_mutual"] is True


class TestGetFollowFeed:
  """フォロー中フィード取得のテスト"""

  def test_get_follow_feed_success(self, follow_service):
    """フォロー中ユーザーの新着レシピを取得"""
    follow_service.follow_user("user_1", "user_2")
    follow_service.follow_user("user_1", "user_3")

    feed = follow_service.get_follow_feed("user_1", limit=20)

    assert len(feed) == 3
    # 新しい順に並んでいることを確認
    assert feed[0]["id"] == "recipe_3"
    assert feed[1]["id"] == "recipe_2"
    assert feed[2]["id"] == "recipe_1"

    # ユーザー情報が含まれることを確認
    assert "user" in feed[0]
    assert feed[0]["user"]["username"] == "charlie"

  def test_get_follow_feed_empty(self, follow_service):
    """フォロー中ユーザーがいない場合は空リスト"""
    feed = follow_service.get_follow_feed("user_1", limit=20)
    assert feed == []

  def test_get_follow_feed_limit(self, follow_service):
    """limit パラメータが機能する"""
    follow_service.follow_user("user_1", "user_2")
    follow_service.follow_user("user_1", "user_3")

    feed = follow_service.get_follow_feed("user_1", limit=2)
    assert len(feed) == 2


class TestGetSuggestedUsers:
  """おすすめユーザー取得のテスト"""

  def test_get_suggested_users_friend_of_friends(self, follow_service):
    """友達の友達をおすすめ"""
    # user_1 -> user_2 -> user_3
    follow_service.follow_user("user_1", "user_2")
    follow_service.follow_user("user_2", "user_3")

    suggestions = follow_service.get_suggested_users("user_1", limit=10)

    # user_3 がおすすめされる
    suggested_ids = [u["id"] for u in suggestions]
    assert "user_3" in suggested_ids

    # common_friends が含まれる
    user_3 = next(u for u in suggestions if u["id"] == "user_3")
    assert "common_friends" in user_3
    assert user_3["common_friends"] == 1

  def test_get_suggested_users_exclude_following(self, follow_service):
    """既にフォロー中のユーザーは除外"""
    follow_service.follow_user("user_1", "user_2")

    suggestions = follow_service.get_suggested_users("user_1", limit=10)

    suggested_ids = [u["id"] for u in suggestions]
    assert "user_2" not in suggested_ids

  def test_get_suggested_users_exclude_self(self, follow_service):
    """自分自身は除外"""
    suggestions = follow_service.get_suggested_users("user_1", limit=10)

    suggested_ids = [u["id"] for u in suggestions]
    assert "user_1" not in suggested_ids

  def test_get_suggested_users_by_recipe_count(self, follow_service):
    """友達の友達が少ない場合はレシピ数でソート"""
    suggestions = follow_service.get_suggested_users("user_1", limit=10)

    # レシピ数が含まれる
    assert all("recipe_count" in u for u in suggestions)

    # user_2 が最もレシピが多い（2件）
    assert suggestions[0]["id"] == "user_2"


class TestGetFollowerCount:
  """フォロワー数取得のテスト"""

  def test_get_follower_count(self, follow_service):
    """フォロワー数を取得"""
    follow_service.follow_user("user_1", "user_2")
    follow_service.follow_user("user_3", "user_2")

    count = follow_service.get_follower_count("user_2")
    assert count == 2


class TestGetFollowingCount:
  """フォロー中数取得のテスト"""

  def test_get_following_count(self, follow_service):
    """フォロー中数を取得"""
    follow_service.follow_user("user_1", "user_2")
    follow_service.follow_user("user_1", "user_3")

    count = follow_service.get_following_count("user_1")
    assert count == 2
