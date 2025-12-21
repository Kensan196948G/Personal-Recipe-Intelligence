"""
API Key Management Service

APIキーの発行・管理・検証を行うサービス
Argon2idを使用したセキュアなハッシュ化
"""

import hashlib
import secrets
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict

# Argon2をインポート（フォールバック付き）
try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError, InvalidHashError
    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False
    PasswordHasher = None
    VerifyMismatchError = Exception
    InvalidHashError = Exception

logger = logging.getLogger(__name__)


@dataclass
class APIKeyScope:
    """APIキーのスコープ定義"""

    read_recipes: bool = True
    write_recipes: bool = False
    delete_recipes: bool = False
    read_tags: bool = True
    write_tags: bool = False


@dataclass
class RateLimit:
    """レート制限設定"""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000


@dataclass
class APIKey:
    """APIキー情報"""

    key_id: str
    key_hash: str
    name: str
    scope: APIKeyScope
    rate_limit: RateLimit
    created_at: str
    last_used_at: Optional[str] = None
    usage_count: int = 0
    is_active: bool = True


@dataclass
class UsageRecord:
    """使用量記録"""

    timestamp: float
    endpoint: str
    status_code: int


class APIKeyService:
    """
    APIキー管理サービス

    機能:
    - APIキーの発行・削除
    - レート制限チェック
    - 使用量トラッキング
    - スコープ検証
    - Argon2idによるセキュアなハッシュ化
    """

    def __init__(self, data_dir: str = "data/api_keys"):
        """
        初期化

        Args:
          data_dir: データ保存ディレクトリ
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.keys_file = self.data_dir / "keys.json"
        self.usage_file = self.data_dir / "usage.json"

        self.keys: Dict[str, APIKey] = {}
        self.usage: Dict[str, List[UsageRecord]] = {}

        # Argon2ハッシャーを初期化（利用可能な場合）
        if ARGON2_AVAILABLE:
            self._hasher = PasswordHasher(
                time_cost=3,
                memory_cost=65536,
                parallelism=4,
                hash_len=32,
                salt_len=16
            )
            logger.info("API Key Service initialized with Argon2id hashing")
        else:
            self._hasher = None
            logger.warning("Argon2 not available, falling back to SHA-256 (less secure)")

        self._load_data()

    def _load_data(self) -> None:
        """保存データの読み込み"""
        # APIキー読み込み
        if self.keys_file.exists():
            try:
                with open(self.keys_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for key_id, key_data in data.items():
                        # スコープとレート制限を復元
                        key_data["scope"] = APIKeyScope(**key_data["scope"])
                        key_data["rate_limit"] = RateLimit(**key_data["rate_limit"])
                        self.keys[key_id] = APIKey(**key_data)
            except Exception as e:
                print(f"Failed to load API keys: {e}")

        # 使用量記録読み込み
        if self.usage_file.exists():
            try:
                with open(self.usage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for key_id, records in data.items():
                        self.usage[key_id] = [
                            UsageRecord(**record) for record in records
                        ]
            except Exception as e:
                print(f"Failed to load usage records: {e}")

    def _save_keys(self) -> None:
        """APIキーの保存"""
        data = {}
        for key_id, api_key in self.keys.items():
            key_dict = asdict(api_key)
            # スコープとレート制限を辞書化
            key_dict["scope"] = asdict(api_key.scope)
            key_dict["rate_limit"] = asdict(api_key.rate_limit)
            data[key_id] = key_dict

        with open(self.keys_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _save_usage(self) -> None:
        """使用量記録の保存"""
        data = {}
        for key_id, records in self.usage.items():
            data[key_id] = [asdict(record) for record in records]

        with open(self.usage_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _hash_key(self, raw_key: str) -> str:
        """
        APIキーをハッシュ化

        Argon2idが利用可能な場合はそれを使用、そうでなければSHA-256にフォールバック

        Args:
            raw_key: 生のAPIキー文字列

        Returns:
            ハッシュ化されたキー
        """
        if self._hasher:
            return self._hasher.hash(raw_key)
        else:
            return hashlib.sha256(raw_key.encode()).hexdigest()

    def _verify_key_hash(self, raw_key: str, key_hash: str) -> bool:
        """
        APIキーのハッシュを検証

        Argon2形式とSHA-256形式の両方に対応（後方互換性）

        Args:
            raw_key: 検証する生のAPIキー
            key_hash: 保存されているハッシュ

        Returns:
            検証成功の場合True
        """
        # Argon2形式のハッシュかチェック（$argon2で始まる）
        if key_hash.startswith("$argon2") and self._hasher:
            try:
                self._hasher.verify(key_hash, raw_key)
                return True
            except (VerifyMismatchError, InvalidHashError):
                return False
        else:
            # SHA-256形式（後方互換性）
            sha256_hash = hashlib.sha256(raw_key.encode()).hexdigest()
            return sha256_hash == key_hash

    def _needs_rehash(self, key_hash: str) -> bool:
        """
        ハッシュの再計算が必要かチェック

        SHA-256からArgon2への移行をサポート

        Args:
            key_hash: 現在のハッシュ

        Returns:
            再ハッシュが必要な場合True
        """
        if not self._hasher:
            return False

        # Argon2でない場合は再ハッシュ推奨
        if not key_hash.startswith("$argon2"):
            return True

        # Argon2のパラメータ更新チェック
        try:
            return self._hasher.check_needs_rehash(key_hash)
        except Exception:
            return False

    def generate_api_key(
        self,
        name: str,
        scope: Optional[APIKeyScope] = None,
        rate_limit: Optional[RateLimit] = None,
    ) -> Tuple[str, APIKey]:
        """
        新しいAPIキーを生成

        Args:
          name: キーの名前（識別用）
          scope: アクセススコープ
          rate_limit: レート制限設定

        Returns:
          (生成されたAPIキー文字列, APIKey情報)
        """
        # 32バイトのランダムキー生成
        raw_key = secrets.token_urlsafe(32)

        # キーIDとハッシュ生成（Argon2idを使用）
        key_id = secrets.token_urlsafe(16)
        key_hash = self._hash_key(raw_key)

        # デフォルト値設定
        if scope is None:
            scope = APIKeyScope()
        if rate_limit is None:
            rate_limit = RateLimit()

        # APIキー情報作成
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            scope=scope,
            rate_limit=rate_limit,
            created_at=datetime.now().isoformat(),
        )

        # 保存
        self.keys[key_id] = api_key
        self.usage[key_id] = []
        self._save_keys()
        self._save_usage()

        return raw_key, api_key

    def verify_api_key(self, raw_key: str) -> Optional[APIKey]:
        """
        APIキーを検証

        Argon2id形式とSHA-256形式の両方に対応（後方互換性）
        SHA-256形式のキーは自動的にArgon2idに移行

        Args:
          raw_key: 検証するAPIキー文字列

        Returns:
          APIKey情報（無効な場合はNone）
        """
        for api_key in self.keys.values():
            if not api_key.is_active:
                continue

            # Argon2id/SHA-256両対応の検証
            if self._verify_key_hash(raw_key, api_key.key_hash):
                # SHA-256からArgon2idへの自動移行
                if self._needs_rehash(api_key.key_hash):
                    logger.info(f"Rehashing API key {api_key.key_id} from SHA-256 to Argon2id")
                    api_key.key_hash = self._hash_key(raw_key)
                    self._save_keys()

                return api_key

        return None

    def revoke_api_key(self, key_id: str) -> bool:
        """
        APIキーを無効化

        Args:
          key_id: キーID

        Returns:
          成功したかどうか
        """
        if key_id in self.keys:
            self.keys[key_id].is_active = False
            self._save_keys()
            return True
        return False

    def delete_api_key(self, key_id: str) -> bool:
        """
        APIキーを削除

        Args:
          key_id: キーID

        Returns:
          成功したかどうか
        """
        if key_id in self.keys:
            del self.keys[key_id]
            if key_id in self.usage:
                del self.usage[key_id]
            self._save_keys()
            self._save_usage()
            return True
        return False

    def list_api_keys(self) -> List[Dict]:
        """
        すべてのAPIキーを一覧取得（ハッシュは除外）

        Returns:
          APIキー情報のリスト
        """
        result = []
        for api_key in self.keys.values():
            key_dict = asdict(api_key)
            # セキュリティのためハッシュは除外
            del key_dict["key_hash"]
            key_dict["scope"] = asdict(api_key.scope)
            key_dict["rate_limit"] = asdict(api_key.rate_limit)
            result.append(key_dict)
        return result

    def check_rate_limit(self, key_id: str) -> Tuple[bool, Optional[str]]:
        """
        レート制限をチェック

        Args:
          key_id: キーID

        Returns:
          (制限内かどうか, エラーメッセージ)
        """
        if key_id not in self.keys:
            return False, "Invalid API key"

        api_key = self.keys[key_id]
        if not api_key.is_active:
            return False, "API key is inactive"

        # 使用量記録を取得
        records = self.usage.get(key_id, [])
        now = time.time()

        # 古い記録を削除（24時間以上前）
        cutoff = now - 86400  # 24 hours
        records = [r for r in records if r.timestamp > cutoff]
        self.usage[key_id] = records

        # 分単位チェック
        minute_ago = now - 60
        minute_count = sum(1 for r in records if r.timestamp > minute_ago)
        if minute_count >= api_key.rate_limit.requests_per_minute:
            return (
                False,
                f"Rate limit exceeded: {api_key.rate_limit.requests_per_minute} requests per minute",
            )

        # 時間単位チェック
        hour_ago = now - 3600
        hour_count = sum(1 for r in records if r.timestamp > hour_ago)
        if hour_count >= api_key.rate_limit.requests_per_hour:
            return (
                False,
                f"Rate limit exceeded: {api_key.rate_limit.requests_per_hour} requests per hour",
            )

        # 日単位チェック
        day_ago = now - 86400
        day_count = sum(1 for r in records if r.timestamp > day_ago)
        if day_count >= api_key.rate_limit.requests_per_day:
            return (
                False,
                f"Rate limit exceeded: {api_key.rate_limit.requests_per_day} requests per day",
            )

        return True, None

    def record_usage(self, key_id: str, endpoint: str, status_code: int) -> None:
        """
        使用量を記録

        Args:
          key_id: キーID
          endpoint: エンドポイント
          status_code: ステータスコード
        """
        if key_id not in self.keys:
            return

        # 使用量記録を追加
        record = UsageRecord(
            timestamp=time.time(), endpoint=endpoint, status_code=status_code
        )

        if key_id not in self.usage:
            self.usage[key_id] = []

        self.usage[key_id].append(record)

        # キーの最終使用日時と使用回数を更新
        self.keys[key_id].last_used_at = datetime.now().isoformat()
        self.keys[key_id].usage_count += 1

        # 保存（パフォーマンスのため非同期化を検討）
        self._save_keys()
        self._save_usage()

    def get_usage_stats(self, key_id: str) -> Optional[Dict]:
        """
        使用量統計を取得

        Args:
          key_id: キーID

        Returns:
          統計情報
        """
        if key_id not in self.keys:
            return None

        records = self.usage.get(key_id, [])
        now = time.time()

        # 時間範囲別の集計
        minute_ago = now - 60
        hour_ago = now - 3600
        day_ago = now - 86400

        minute_count = sum(1 for r in records if r.timestamp > minute_ago)
        hour_count = sum(1 for r in records if r.timestamp > hour_ago)
        day_count = sum(1 for r in records if r.timestamp > day_ago)

        # レート制限情報
        api_key = self.keys[key_id]

        return {
            "key_id": key_id,
            "total_requests": api_key.usage_count,
            "last_used_at": api_key.last_used_at,
            "current_usage": {
                "last_minute": minute_count,
                "last_hour": hour_count,
                "last_day": day_count,
            },
            "rate_limits": {
                "per_minute": api_key.rate_limit.requests_per_minute,
                "per_hour": api_key.rate_limit.requests_per_hour,
                "per_day": api_key.rate_limit.requests_per_day,
            },
            "remaining": {
                "per_minute": api_key.rate_limit.requests_per_minute - minute_count,
                "per_hour": api_key.rate_limit.requests_per_hour - hour_count,
                "per_day": api_key.rate_limit.requests_per_day - day_count,
            },
        }

    def check_scope(self, key_id: str, required_scope: str) -> bool:
        """
        スコープをチェック

        Args:
          key_id: キーID
          required_scope: 必要なスコープ（例: "write_recipes"）

        Returns:
          スコープがあるかどうか
        """
        if key_id not in self.keys:
            return False

        api_key = self.keys[key_id]
        scope = api_key.scope

        return getattr(scope, required_scope, False)

    def rotate_api_key(self, key_id: str) -> Optional[Tuple[str, APIKey]]:
        """
        APIキーをローテーション（新しいキーを生成し、古いキーを無効化）

        Args:
          key_id: 既存のキーID

        Returns:
          (新しいAPIキー文字列, 新しいAPIKey情報)
        """
        if key_id not in self.keys:
            return None

        old_key = self.keys[key_id]

        # 新しいキーを同じ設定で生成
        new_raw_key, new_api_key = self.generate_api_key(
            name=f"{old_key.name} (rotated)",
            scope=old_key.scope,
            rate_limit=old_key.rate_limit,
        )

        # 古いキーを無効化
        self.revoke_api_key(key_id)

        return new_raw_key, new_api_key
