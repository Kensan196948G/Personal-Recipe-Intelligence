"""
Recipe Sharing Service
レシピ共有機能を提供するサービス
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class SharePermission(str, Enum):
    """共有権限"""

    VIEW_ONLY = "view_only"
    EDIT = "edit"


@dataclass
class RecipeShare:
    """レシピ共有情報"""

    share_id: str
    recipe_id: str
    owner_id: str
    permission: SharePermission
    created_at: str
    expires_at: Optional[str]
    shared_with: Optional[List[str]]  # メールアドレスまたはユーザーID
    share_link: str
    is_active: bool
    access_count: int
    last_accessed: Optional[str]


class RecipeSharingService:
    """レシピ共有サービス"""

    def __init__(self, data_dir: str = "data/shares"):
        """
        初期化

        Args:
          data_dir: 共有データディレクトリ
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.shares_file = self.data_dir / "shares.json"
        self.history_file = self.data_dir / "share_history.json"
        self._ensure_files()

    def _ensure_files(self) -> None:
        """必要なファイルを作成"""
        if not self.shares_file.exists():
            self.shares_file.write_text(json.dumps({"shares": []}, indent=2))
        if not self.history_file.exists():
            self.history_file.write_text(json.dumps({"history": []}, indent=2))

    def _load_shares(self) -> List[Dict[str, Any]]:
        """共有データを読み込み"""
        try:
            data = json.loads(self.shares_file.read_text())
            return data.get("shares", [])
        except Exception as e:
            print(f"Error loading shares: {e}")
            return []

    def _save_shares(self, shares: List[Dict[str, Any]]) -> None:
        """共有データを保存"""
        try:
            self.shares_file.write_text(
                json.dumps({"shares": shares}, indent=2, ensure_ascii=False)
            )
        except Exception as e:
            print(f"Error saving shares: {e}")
            raise

    def _load_history(self) -> List[Dict[str, Any]]:
        """共有履歴を読み込み"""
        try:
            data = json.loads(self.history_file.read_text())
            return data.get("history", [])
        except Exception as e:
            print(f"Error loading history: {e}")
            return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        """共有履歴を保存"""
        try:
            self.history_file.write_text(
                json.dumps({"history": history}, indent=2, ensure_ascii=False)
            )
        except Exception as e:
            print(f"Error saving history: {e}")

    def _add_history_entry(
        self,
        share_id: str,
        action: str,
        user_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """履歴エントリを追加"""
        history = self._load_history()
        entry = {
            "share_id": share_id,
            "action": action,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        }
        history.append(entry)
        self._save_history(history)

    def create_share_link(
        self,
        recipe_id: str,
        owner_id: str,
        permission: SharePermission = SharePermission.VIEW_ONLY,
        expires_in_days: int = 7,
        shared_with: Optional[List[str]] = None,
    ) -> RecipeShare:
        """
        共有リンクを作成

        Args:
          recipe_id: レシピID
          owner_id: オーナーユーザーID
          permission: 共有権限
          expires_in_days: 有効期限（日数）
          shared_with: 共有相手リスト

        Returns:
          RecipeShare: 作成された共有情報
        """
        share_id = str(uuid.uuid4())
        now = datetime.now()
        expires_at = (
            (now + timedelta(days=expires_in_days)).isoformat()
            if expires_in_days > 0
            else None
        )

        share = RecipeShare(
            share_id=share_id,
            recipe_id=recipe_id,
            owner_id=owner_id,
            permission=permission,
            created_at=now.isoformat(),
            expires_at=expires_at,
            shared_with=shared_with or [],
            share_link=f"/shared/{share_id}",
            is_active=True,
            access_count=0,
            last_accessed=None,
        )

        shares = self._load_shares()
        shares.append(asdict(share))
        self._save_shares(shares)

        # 履歴に記録
        self._add_history_entry(
            share_id=share_id,
            action="created",
            user_id=owner_id,
            details={
                "recipe_id": recipe_id,
                "permission": permission.value,
                "expires_at": expires_at,
            },
        )

        return share

    def get_share_by_id(self, share_id: str) -> Optional[RecipeShare]:
        """
        共有IDで共有情報を取得

        Args:
          share_id: 共有ID

        Returns:
          Optional[RecipeShare]: 共有情報
        """
        shares = self._load_shares()
        for share_data in shares:
            if share_data["share_id"] == share_id:
                # 有効期限チェック
                if share_data["is_active"]:
                    if share_data["expires_at"]:
                        expires_at = datetime.fromisoformat(share_data["expires_at"])
                        if datetime.now() > expires_at:
                            # 期限切れ
                            share_data["is_active"] = False
                            self._save_shares(shares)
                            return None

                    # アクセスカウント更新
                    share_data["access_count"] += 1
                    share_data["last_accessed"] = datetime.now().isoformat()
                    self._save_shares(shares)

                    return RecipeShare(**share_data)
        return None

    def get_shares_by_recipe(self, recipe_id: str) -> List[RecipeShare]:
        """
        レシピIDで共有情報リストを取得

        Args:
          recipe_id: レシピID

        Returns:
          List[RecipeShare]: 共有情報リスト
        """
        shares = self._load_shares()
        result = []
        for share_data in shares:
            if share_data["recipe_id"] == recipe_id and share_data["is_active"]:
                result.append(RecipeShare(**share_data))
        return result

    def get_shares_by_owner(self, owner_id: str) -> List[RecipeShare]:
        """
        オーナーIDで共有情報リストを取得（自分が共有したレシピ）

        Args:
          owner_id: オーナーユーザーID

        Returns:
          List[RecipeShare]: 共有情報リスト
        """
        shares = self._load_shares()
        result = []
        for share_data in shares:
            if share_data["owner_id"] == owner_id and share_data["is_active"]:
                result.append(RecipeShare(**share_data))
        return result

    def get_shares_with_user(self, user_id: str) -> List[RecipeShare]:
        """
        ユーザーIDで共有情報リストを取得（自分に共有されたレシピ）

        Args:
          user_id: ユーザーID（メールアドレスまたはユーザーID）

        Returns:
          List[RecipeShare]: 共有情報リスト
        """
        shares = self._load_shares()
        result = []
        for share_data in shares:
            if share_data["is_active"]:
                shared_with = share_data.get("shared_with", [])
                if user_id in shared_with:
                    result.append(RecipeShare(**share_data))
        return result

    def update_share(
        self,
        share_id: str,
        permission: Optional[SharePermission] = None,
        expires_in_days: Optional[int] = None,
        shared_with: Optional[List[str]] = None,
    ) -> Optional[RecipeShare]:
        """
        共有情報を更新

        Args:
          share_id: 共有ID
          permission: 共有権限
          expires_in_days: 有効期限（日数）
          shared_with: 共有相手リスト

        Returns:
          Optional[RecipeShare]: 更新後の共有情報
        """
        shares = self._load_shares()
        for share_data in shares:
            if share_data["share_id"] == share_id:
                if permission:
                    share_data["permission"] = permission.value
                if expires_in_days is not None:
                    if expires_in_days > 0:
                        expires_at = (
                            datetime.now() + timedelta(days=expires_in_days)
                        ).isoformat()
                        share_data["expires_at"] = expires_at
                    else:
                        share_data["expires_at"] = None
                if shared_with is not None:
                    share_data["shared_with"] = shared_with

                self._save_shares(shares)

                # 履歴に記録
                self._add_history_entry(
                    share_id=share_id,
                    action="updated",
                    user_id=share_data["owner_id"],
                    details={
                        "permission": share_data["permission"],
                        "expires_at": share_data.get("expires_at"),
                    },
                )

                return RecipeShare(**share_data)
        return None

    def revoke_share(self, share_id: str, user_id: str) -> bool:
        """
        共有を解除

        Args:
          share_id: 共有ID
          user_id: 実行ユーザーID

        Returns:
          bool: 成功/失敗
        """
        shares = self._load_shares()
        for share_data in shares:
            if share_data["share_id"] == share_id:
                if share_data["owner_id"] == user_id:
                    share_data["is_active"] = False
                    self._save_shares(shares)

                    # 履歴に記録
                    self._add_history_entry(
                        share_id=share_id,
                        action="revoked",
                        user_id=user_id,
                        details={"recipe_id": share_data["recipe_id"]},
                    )

                    return True
        return False

    def get_share_history(self, share_id: str) -> List[Dict[str, Any]]:
        """
        共有履歴を取得

        Args:
          share_id: 共有ID

        Returns:
          List[Dict[str, Any]]: 履歴エントリリスト
        """
        history = self._load_history()
        return [entry for entry in history if entry["share_id"] == share_id]

    def cleanup_expired_shares(self) -> int:
        """
        期限切れの共有を無効化

        Returns:
          int: 無効化した共有数
        """
        shares = self._load_shares()
        now = datetime.now()
        count = 0

        for share_data in shares:
            if share_data["is_active"] and share_data["expires_at"]:
                expires_at = datetime.fromisoformat(share_data["expires_at"])
                if now > expires_at:
                    share_data["is_active"] = False
                    count += 1

        if count > 0:
            self._save_shares(shares)

        return count

    def get_share_stats(self, owner_id: str) -> Dict[str, Any]:
        """
        共有統計情報を取得

        Args:
          owner_id: オーナーユーザーID

        Returns:
          Dict[str, Any]: 統計情報
        """
        shares = self.get_shares_by_owner(owner_id)
        total_accesses = sum(share.access_count for share in shares)

        return {
            "total_shares": len(shares),
            "active_shares": len([s for s in shares if s.is_active]),
            "total_accesses": total_accesses,
            "view_only_shares": len(
                [s for s in shares if s.permission == SharePermission.VIEW_ONLY]
            ),
            "edit_shares": len(
                [s for s in shares if s.permission == SharePermission.EDIT]
            ),
        }
