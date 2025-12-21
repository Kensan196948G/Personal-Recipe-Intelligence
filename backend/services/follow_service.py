"""
Follow Service - ユーザーフォロー関連の処理
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class FollowService:
    """フォロー管理サービス"""

    def __init__(self, data_dir: str = "data"):
        """
        初期化

        Args:
            data_dir: データディレクトリパス
        """
        self.data_dir = Path(data_dir)
        self.follow_file = self.data_dir / "follows.json"
        self.users_file = self.data_dir / "users.json"
        self.recipes_file = self.data_dir / "recipes.json"
        self._ensure_data_files()

    def _ensure_data_files(self) -> None:
        """データファイルの存在確認と初期化"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if not self.follow_file.exists():
            self._save_follows([])

        if not self.users_file.exists():
            self._save_users([])

        if not self.recipes_file.exists():
            self._save_recipes([])

    def _load_follows(self) -> List[Dict]:
        """フォロー関係データを読み込む"""
        with open(self.follow_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_follows(self, follows: List[Dict]) -> None:
        """フォロー関係データを保存"""
        with open(self.follow_file, "w", encoding="utf-8") as f:
            json.dump(follows, f, ensure_ascii=False, indent=2)

    def _load_users(self) -> List[Dict]:
        """ユーザーデータを読み込む"""
        with open(self.users_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_users(self, users: List[Dict]) -> None:
        """ユーザーデータを保存"""
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

    def _load_recipes(self) -> List[Dict]:
        """レシピデータを読み込む"""
        with open(self.recipes_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_recipes(self, recipes: List[Dict]) -> None:
        """レシピデータを保存"""
        with open(self.recipes_file, "w", encoding="utf-8") as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)

    def _get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """ユーザーIDでユーザーを取得"""
        users = self._load_users()
        return next((u for u in users if u.get("id") == user_id), None)

    def follow_user(self, follower_id: str, following_id: str) -> Dict:
        """
        ユーザーをフォロー

        Args:
            follower_id: フォローするユーザーID
            following_id: フォローされるユーザーID

        Returns:
            フォロー関係データ

        Raises:
            ValueError: 自分自身をフォロー、またはユーザーが存在しない場合
        """
        if follower_id == following_id:
            raise ValueError("自分自身をフォローすることはできません")

        # ユーザーの存在確認
        follower = self._get_user_by_id(follower_id)
        following = self._get_user_by_id(following_id)

        if not follower:
            raise ValueError(f"フォロワーユーザー {follower_id} が存在しません")
        if not following:
            raise ValueError(f"フォロー対象ユーザー {following_id} が存在しません")

        follows = self._load_follows()

        # 既にフォロー済みかチェック
        existing = next(
            (
                f
                for f in follows
                if f.get("follower_id") == follower_id
                and f.get("following_id") == following_id
            ),
            None,
        )

        if existing:
            return existing

        # 新規フォロー関係を作成
        follow_data = {
            "id": f"{follower_id}_{following_id}_{datetime.now().timestamp()}",
            "follower_id": follower_id,
            "following_id": following_id,
            "created_at": datetime.now().isoformat(),
        }

        follows.append(follow_data)
        self._save_follows(follows)

        return follow_data

    def unfollow_user(self, follower_id: str, following_id: str) -> bool:
        """
        ユーザーをアンフォロー

        Args:
            follower_id: フォロー解除するユーザーID
            following_id: フォロー解除されるユーザーID

        Returns:
            成功した場合True、フォロー関係が存在しない場合False
        """
        follows = self._load_follows()

        # フォロー関係を検索
        original_len = len(follows)
        follows = [
            f
            for f in follows
            if not (
                f.get("follower_id") == follower_id
                and f.get("following_id") == following_id
            )
        ]

        if len(follows) == original_len:
            return False

        self._save_follows(follows)
        return True

    def get_followers(self, user_id: str, limit: int = 100, offset: int = 0) -> Dict:
        """
        フォロワー一覧を取得

        Args:
            user_id: 対象ユーザーID
            limit: 取得件数
            offset: オフセット

        Returns:
            フォロワー情報とメタデータ
        """
        follows = self._load_follows()
        users = self._load_users()

        # このユーザーをフォローしている関係を抽出
        follower_relations = [f for f in follows if f.get("following_id") == user_id]

        # フォロワーIDリストを取得
        follower_ids = [f.get("follower_id") for f in follower_relations]

        # フォロワーユーザー情報を取得
        followers = [u for u in users if u.get("id") in follower_ids]

        # 相互フォロー情報を追加
        for follower in followers:
            follower["is_mutual"] = self.is_mutual_follow(follower.get("id"), user_id)
            follower["is_following"] = self.is_following(user_id, follower.get("id"))

        # ページネーション
        total = len(followers)
        followers = followers[offset : offset + limit]

        return {
            "followers": followers,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def get_following(self, user_id: str, limit: int = 100, offset: int = 0) -> Dict:
        """
        フォロー中ユーザー一覧を取得

        Args:
            user_id: 対象ユーザーID
            limit: 取得件数
            offset: オフセット

        Returns:
            フォロー中ユーザー情報とメタデータ
        """
        follows = self._load_follows()
        users = self._load_users()

        # このユーザーがフォローしている関係を抽出
        following_relations = [f for f in follows if f.get("follower_id") == user_id]

        # フォロー中ユーザーIDリストを取得
        following_ids = [f.get("following_id") for f in following_relations]

        # フォロー中ユーザー情報を取得
        following_users = [u for u in users if u.get("id") in following_ids]

        # 相互フォロー情報を追加
        for user in following_users:
            user["is_mutual"] = self.is_mutual_follow(user_id, user.get("id"))
            user["is_follower"] = self.is_following(user.get("id"), user_id)

        # ページネーション
        total = len(following_users)
        following_users = following_users[offset : offset + limit]

        return {
            "following": following_users,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def is_following(self, follower_id: str, following_id: str) -> bool:
        """
        フォロー関係をチェック

        Args:
            follower_id: フォロワーID
            following_id: フォロー対象ID

        Returns:
            フォロー中の場合True
        """
        follows = self._load_follows()
        return any(
            f.get("follower_id") == follower_id
            and f.get("following_id") == following_id
            for f in follows
        )

    def is_mutual_follow(self, user_id_1: str, user_id_2: str) -> bool:
        """
        相互フォロー判定

        Args:
            user_id_1: ユーザー1のID
            user_id_2: ユーザー2のID

        Returns:
            相互フォローの場合True
        """
        return self.is_following(user_id_1, user_id_2) and self.is_following(
            user_id_2, user_id_1
        )

    def get_follow_status(self, current_user_id: str, target_user_id: str) -> Dict:
        """
        フォロー状態を取得

        Args:
            current_user_id: 現在のユーザーID
            target_user_id: 対象ユーザーID

        Returns:
            フォロー状態情報
        """
        follows = self._load_follows()

        # フォロワー数・フォロー中数を計算
        follower_count = sum(
            1 for f in follows if f.get("following_id") == target_user_id
        )
        following_count = sum(
            1 for f in follows if f.get("follower_id") == target_user_id
        )

        return {
            "is_following": self.is_following(current_user_id, target_user_id),
            "is_follower": self.is_following(target_user_id, current_user_id),
            "is_mutual": self.is_mutual_follow(current_user_id, target_user_id),
            "follower_count": follower_count,
            "following_count": following_count,
        }

    def get_follow_feed(self, user_id: str, limit: int = 20) -> List[Dict]:
        """
        フォロー中ユーザーの新着レシピを取得

        Args:
            user_id: ユーザーID
            limit: 取得件数（デフォルト: 20）

        Returns:
            新着レシピリスト
        """
        follows = self._load_follows()
        recipes = self._load_recipes()
        users = self._load_users()

        # フォロー中ユーザーIDリストを取得
        following_ids = [
            f.get("following_id") for f in follows if f.get("follower_id") == user_id
        ]

        if not following_ids:
            return []

        # フォロー中ユーザーのレシピを抽出
        following_recipes = [r for r in recipes if r.get("user_id") in following_ids]

        # 作成日時でソート（新しい順）
        following_recipes.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        # ユーザー情報を追加
        user_map = {u.get("id"): u for u in users}
        for recipe in following_recipes[:limit]:
            user_id_recipe = recipe.get("user_id")
            if user_id_recipe in user_map:
                recipe["user"] = {
                    "id": user_map[user_id_recipe].get("id"),
                    "username": user_map[user_id_recipe].get("username"),
                    "display_name": user_map[user_id_recipe].get("display_name"),
                    "avatar_url": user_map[user_id_recipe].get("avatar_url"),
                }

        return following_recipes[:limit]

    def get_suggested_users(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        おすすめユーザーを提案

        Args:
            user_id: 現在のユーザーID
            limit: 取得件数

        Returns:
            おすすめユーザーリスト
        """
        follows = self._load_follows()
        users = self._load_users()
        recipes = self._load_recipes()

        # フォロー中ユーザーIDリストを取得
        following_ids = [
            f.get("following_id") for f in follows if f.get("follower_id") == user_id
        ]

        # 自分とフォロー中ユーザーを除外
        excluded_ids = set(following_ids + [user_id])

        # フォロー中ユーザーがフォローしているユーザー（友達の友達）
        friend_of_friends = []
        for following_id in following_ids:
            friend_follows = [
                f.get("following_id")
                for f in follows
                if f.get("follower_id") == following_id
                and f.get("following_id") not in excluded_ids
            ]
            friend_of_friends.extend(friend_follows)

        # 出現回数でカウント（共通の友達が多い順）
        from collections import Counter

        suggested_ids = Counter(friend_of_friends).most_common()

        # ユーザー情報を取得
        suggested_users = []
        for suggested_id, common_count in suggested_ids[:limit]:
            user = self._get_user_by_id(suggested_id)
            if user:
                # レシピ数を追加
                recipe_count = sum(
                    1 for r in recipes if r.get("user_id") == suggested_id
                )
                user["recipe_count"] = recipe_count
                user["common_friends"] = common_count
                suggested_users.append(user)

        # 友達の友達が少ない場合、レシピ数が多いユーザーを追加
        if len(suggested_users) < limit:
            remaining = limit - len(suggested_users)
            suggested_user_ids = {u["id"] for u in suggested_users}

            # レシピ数でユーザーをソート
            all_users = [
                u
                for u in users
                if u.get("id") not in excluded_ids
                and u.get("id") not in suggested_user_ids
            ]

            for user in all_users:
                user["recipe_count"] = sum(
                    1 for r in recipes if r.get("user_id") == user.get("id")
                )

            all_users.sort(key=lambda x: x.get("recipe_count", 0), reverse=True)
            suggested_users.extend(all_users[:remaining])

        return suggested_users[:limit]

    def get_follower_count(self, user_id: str) -> int:
        """
        フォロワー数を取得

        Args:
            user_id: ユーザーID

        Returns:
            フォロワー数
        """
        follows = self._load_follows()
        return sum(1 for f in follows if f.get("following_id") == user_id)

    def get_following_count(self, user_id: str) -> int:
        """
        フォロー中数を取得

        Args:
            user_id: ユーザーID

        Returns:
            フォロー中数
        """
        follows = self._load_follows()
        return sum(1 for f in follows if f.get("follower_id") == user_id)
