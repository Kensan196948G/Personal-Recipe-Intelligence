# Audit Logging Guide - Personal Recipe Intelligence

監査ログシステムの実装ガイド

CLAUDE.md Section 6.4 準拠

---

## 概要

Personal Recipe Intelligence の監査ログシステムは、すべてのセキュリティ関連イベントを記録し、データの整合性とセキュリティを保証します。

### 主な機能

- レシピCRUD操作の記録
- 認証・認可イベントの記録
- APIキー操作の記録
- 管理者アクションの記録
- セキュリティイベントの記録

---

## アーキテクチャ

### コンポーネント構成

```
backend/
├── services/
│   └── audit_service.py          # 監査サービス本体
├── middleware/
│   ├── audit_middleware.py       # 監査ミドルウェア
│   └── auth_with_audit.py        # 認証ミドルウェア（監査統合）
├── routes/
│   └── recipes_with_audit.py     # レシピAPI（監査統合例）
└── tests/
    └── test_audit_service.py     # テストスイート

logs/
└── audit.json                    # 監査ログファイル
```

---

## セットアップ

### 1. 依存関係のインストール

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
pip install -r backend/requirements.txt
```

### 2. ログディレクトリの作成

```bash
mkdir -p logs
chmod 700 logs  # セキュリティのため読み取り制限
```

### 3. 環境変数の設定（`.env`）

```env
AUDIT_LOG_DIR=logs
AUDIT_LOG_LEVEL=INFO
```

---

## 基本的な使い方

### 監査サービスの初期化

```python
from backend.services.audit_service import get_audit_service

# シングルトンインスタンスを取得
audit_service = get_audit_service()
```

### レシピ作成の記録

```python
audit_service.log_recipe_create(
    recipe_id="recipe_123",
    user_id="user_001",
    ip_address="192.168.1.100",
    recipe_title="カレーライス"
)
```

### レシピ更新の記録

```python
changes = {
    "updated_fields": ["title", "ingredients"],
    "field_count": 2
}

audit_service.log_recipe_update(
    recipe_id="recipe_123",
    user_id="user_001",
    ip_address="192.168.1.100",
    changes=changes
)
```

### レシピ削除の記録

```python
audit_service.log_recipe_delete(
    recipe_id="recipe_123",
    user_id="user_001",
    ip_address="192.168.1.100",
    recipe_title="カレーライス"
)
```

---

## API統合

### Flask エンドポイントへの統合

```python
from flask import Blueprint, request, jsonify, g
from backend.services.audit_service import get_audit_service
from backend.middleware.audit_middleware import get_client_ip

recipe_bp = Blueprint("recipes", __name__)
audit_service = get_audit_service()

@recipe_bp.route("/api/v1/recipes", methods=["POST"])
def create_recipe():
    data = request.get_json()
    user_id = g.user_id
    ip_address = get_client_ip(request)

    # レシピ作成処理
    recipe_id = db.create_recipe(data)

    # 監査ログ記録
    audit_service.log_recipe_create(
        recipe_id=recipe_id,
        user_id=user_id,
        ip_address=ip_address,
        recipe_title=data.get("title")
    )

    return jsonify({"status": "ok", "data": {"recipe_id": recipe_id}})
```

---

## 認証統合

### 認証ミドルウェアの使用

```python
from backend.middleware.auth_with_audit import require_auth

@recipe_bp.route("/api/v1/recipes", methods=["POST"])
@require_auth  # 自動的に認証成功/失敗を記録
def create_recipe():
    # 認証済みユーザーのみアクセス可能
    user_id = g.user_id
    # ...
```

### APIキー管理

```python
from backend.middleware.auth_with_audit import create_api_key, revoke_api_key

# APIキー生成（自動的に監査ログ記録）
api_key = create_api_key(user_id="user_001", key_name="Production Key")

# APIキー失効（自動的に監査ログ記録）
revoke_api_key(user_id="user_001", key_id="key_abc123")
```

---

## ログ形式

### JSON構造

```json
{
  "timestamp": "2025-12-11T10:30:45.123456+00:00",
  "action": "recipe_create",
  "resource_type": "recipe",
  "status": "success",
  "user_id": "user_001",
  "resource_id": "recipe_123",
  "ip_address": "192.168.1.100",
  "details": {
    "recipe_title": "カレーライス"
  }
}
```

### フィールド説明

| フィールド | 型 | 説明 |
|----------|-----|------|
| `timestamp` | string | ISO8601形式のタイムスタンプ（UTC） |
| `action` | string | 実行されたアクション（例：`recipe_create`） |
| `resource_type` | string | 対象リソースタイプ（例：`recipe`） |
| `status` | string | 実行結果（`success`, `failure`, `blocked`） |
| `user_id` | string | ユーザーID（オプション） |
| `resource_id` | string | リソースID（オプション） |
| `ip_address` | string | クライアントIPアドレス（オプション） |
| `details` | object | 追加詳細情報（オプション） |

---

## セキュリティ機能

### 機密データのマスキング

監査サービスは自動的に機密データをマスクします：

```python
details = {
    "username": "testuser",
    "password": "secret123",  # マスクされる
    "api_key": "key_abc123",  # マスクされる
    "email": "test@example.com"
}

# 記録時に自動マスキング
audit_service.log(
    action=AuditAction.ADMIN_CONFIG_UPDATED,
    resource_type=AuditResourceType.CONFIG,
    details=details
)

# ログには以下のように記録される
# "password": "***MASKED***"
# "api_key": "***MASKED***"
```

### マスキング対象キーワード

- `password`
- `token`
- `api_key`
- `secret`
- `apikey`
- `auth_token`
- `bearer`

---

## 監査イベント一覧

### レシピCRUD

- `recipe_create` - レシピ作成
- `recipe_read` - レシピ読み取り
- `recipe_update` - レシピ更新
- `recipe_delete` - レシピ削除
- `recipe_batch_delete` - レシピ一括削除

### 認証

- `auth_success` - 認証成功
- `auth_failure` - 認証失敗
- `auth_token_created` - トークン作成
- `auth_token_revoked` - トークン失効

### APIキー

- `api_key_created` - APIキー作成
- `api_key_deleted` - APIキー削除
- `api_key_rotated` - APIキーローテーション

### 管理者

- `admin_config_updated` - 設定変更
- `admin_user_created` - ユーザー作成
- `admin_user_deleted` - ユーザー削除
- `admin_backup_created` - バックアップ作成
- `admin_restore_executed` - リストア実行

### セキュリティ

- `security_breach_attempt` - セキュリティ侵害試行
- `security_rate_limit_exceeded` - レート制限超過
- `security_invalid_token` - 無効トークン使用

### データ操作

- `data_import` - データインポート
- `data_export` - データエクスポート
- `data_migration` - データマイグレーション

---

## ログ分析

### ログファイルの読み取り

```bash
# 全ログを表示
cat logs/audit.json

# JSONとして整形表示
cat logs/audit.json | jq '.'

# 特定ユーザーのアクションを抽出
cat logs/audit.json | jq 'select(.user_id == "user_001")'

# 認証失敗のみ抽出
cat logs/audit.json | jq 'select(.action == "auth_failure")'

# 特定日時以降のログを抽出
cat logs/audit.json | jq 'select(.timestamp > "2025-12-11T00:00:00")'
```

### Python での分析

```python
import json
from pathlib import Path

log_file = Path("logs/audit.json")

# すべてのログエントリを読み込み
entries = []
with open(log_file, "r", encoding="utf-8") as f:
    for line in f:
        entries.append(json.loads(line))

# 認証失敗を抽出
auth_failures = [e for e in entries if e["action"] == "auth_failure"]
print(f"認証失敗数: {len(auth_failures)}")

# ユーザー別アクション集計
from collections import Counter
user_actions = Counter(e["user_id"] for e in entries if e.get("user_id"))
print(f"最もアクティブなユーザー: {user_actions.most_common(5)}")
```

---

## テスト

### ユニットテストの実行

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
pytest backend/tests/test_audit_service.py -v
```

### カバレッジレポート

```bash
pytest backend/tests/test_audit_service.py --cov=backend/services/audit_service --cov-report=html
```

---

## パフォーマンス

### スレッドセーフ

監査サービスはスレッドセーフです。複数のリクエストが同時にログを記録しても、データ破損は発生しません。

```python
# Lockを使用した排他制御
with self.lock:
    with open(self.audit_log_path, "a", encoding="utf-8") as f:
        json.dump(audit_entry, f, ensure_ascii=False)
        f.write("\n")
```

### ログローテーション

大量のログが蓄積された場合は、ログローテーションを実施してください：

```bash
# ログファイルをアーカイブ
cd logs
mv audit.json audit_$(date +%Y%m%d_%H%M%S).json
gzip audit_*.json

# 新しいログファイルが自動的に作成される
```

---

## トラブルシューティング

### ログが記録されない

1. ディレクトリ権限を確認
   ```bash
   ls -la logs/
   chmod 700 logs/
   ```

2. ログサービスの初期化を確認
   ```python
   audit_service = get_audit_service()
   print(audit_service.audit_log_path)
   ```

### 緊急ログの確認

監査ログの書き込みに失敗した場合、緊急ログが記録されます：

```bash
cat logs/audit_emergency.json
```

---

## ベストプラクティス

### 1. すべての重要操作を記録

レシピの作成・更新・削除は必ず記録してください。

### 2. IPアドレスを常に記録

セキュリティインシデント調査のため、IPアドレスは必須です。

### 3. 詳細情報を含める

変更内容や理由などの詳細情報を含めることで、監査の有効性が向上します。

### 4. 定期的にログを分析

不審なアクセスパターンや異常な操作を早期に検出してください。

### 5. ログを安全に保管

監査ログは改ざん防止のため、定期的にバックアップを取得してください。

---

## 関連ドキュメント

- [CLAUDE.md](/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/CLAUDE.md) - Section 6.4 監査ログ要件
- [セキュリティガイド](/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/docs/security-guide.md)
- [APIドキュメント](/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/docs/api-documentation.md)

---

## ライセンス

MIT License - Personal Recipe Intelligence Project
