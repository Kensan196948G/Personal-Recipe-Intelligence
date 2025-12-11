# Audit Logging Quick Reference

監査ログ クイックリファレンス

---

## インポート

```python
from backend.services.audit_service import get_audit_service
from backend.middleware.audit_middleware import get_client_ip

audit_service = get_audit_service()
```

---

## レシピ操作

### 作成
```python
audit_service.log_recipe_create(
    recipe_id="recipe_123",
    user_id="user_001",
    ip_address="192.168.1.100",
    recipe_title="カレーライス"
)
```

### 更新
```python
audit_service.log_recipe_update(
    recipe_id="recipe_123",
    user_id="user_001",
    ip_address="192.168.1.100",
    changes={"updated_fields": ["title", "ingredients"]}
)
```

### 削除
```python
audit_service.log_recipe_delete(
    recipe_id="recipe_123",
    user_id="user_001",
    ip_address="192.168.1.100",
    recipe_title="カレーライス"
)
```

### 一括削除
```python
audit_service.log_recipe_batch_delete(
    recipe_ids=["recipe_001", "recipe_002"],
    user_id="user_001",
    ip_address="192.168.1.100"
)
```

---

## 認証

### 成功
```python
audit_service.log_auth_success(
    user_id="user_001",
    ip_address="192.168.1.100",
    method="api_key"
)
```

### 失敗
```python
audit_service.log_auth_failure(
    user_id="user_001",
    ip_address="192.168.1.100",
    reason="invalid_credentials",
    method="api_key"
)
```

### トークン作成
```python
audit_service.log_token_created(
    user_id="user_001",
    token_id="token_abc123",
    ip_address="192.168.1.100",
    expires_at="2025-12-31T23:59:59Z"
)
```

### トークン失効
```python
audit_service.log_token_revoked(
    user_id="user_001",
    token_id="token_abc123",
    ip_address="192.168.1.100",
    reason="user_request"
)
```

---

## APIキー

### 作成
```python
audit_service.log_api_key_created(
    user_id="user_001",
    key_id="key_abc123",
    ip_address="192.168.1.100",
    key_name="Production Key"
)
```

### 削除
```python
audit_service.log_api_key_deleted(
    user_id="user_001",
    key_id="key_abc123",
    ip_address="192.168.1.100",
    key_name="Production Key"
)
```

### ローテーション
```python
audit_service.log_api_key_rotated(
    user_id="user_001",
    old_key_id="key_old",
    new_key_id="key_new",
    ip_address="192.168.1.100"
)
```

---

## 管理者操作

### 設定変更
```python
audit_service.log_admin_config_updated(
    user_id="admin_001",
    config_key="max_recipes",
    ip_address="192.168.1.100",
    old_value=100,
    new_value=200
)
```

### バックアップ作成
```python
audit_service.log_admin_backup_created(
    user_id="admin_001",
    backup_id="backup_20251211",
    ip_address="192.168.1.100",
    backup_size=1024000
)
```

### リストア実行
```python
audit_service.log_admin_restore_executed(
    user_id="admin_001",
    backup_id="backup_20251211",
    ip_address="192.168.1.100"
)
```

---

## セキュリティイベント

### 侵害試行
```python
audit_service.log_security_breach_attempt(
    ip_address="192.168.1.100",
    user_id="user_001",
    attack_type="sql_injection",
    details={"endpoint": "/api/v1/recipes", "payload": "' OR 1=1"}
)
```

### レート制限超過
```python
audit_service.log_rate_limit_exceeded(
    ip_address="192.168.1.100",
    user_id="user_001",
    endpoint="/api/v1/recipes"
)
```

### 無効トークン
```python
audit_service.log_invalid_token(
    ip_address="192.168.1.100",
    user_id="user_001",
    token_prefix="pri_abc1"
)
```

---

## データ操作

### インポート
```python
audit_service.log_data_import(
    user_id="user_001",
    ip_address="192.168.1.100",
    record_count=150,
    source="csv_file"
)
```

### エクスポート
```python
audit_service.log_data_export(
    user_id="user_001",
    ip_address="192.168.1.100",
    record_count=200,
    format="json"
)
```

---

## Flaskデコレータ

### 認証必須
```python
from backend.middleware.auth_with_audit import require_auth

@app.route("/api/v1/recipes", methods=["POST"])
@require_auth  # 自動的に認証ログ記録
def create_recipe():
    user_id = g.user_id
    # ...
```

### 認証オプショナル
```python
from backend.middleware.auth_with_audit import optional_auth

@app.route("/api/v1/recipes", methods=["GET"])
@optional_auth  # 認証があれば検証、なくてもOK
def get_recipes():
    user_id = getattr(g, "user_id", None)
    # ...
```

### レート制限
```python
from backend.middleware.auth_with_audit import rate_limit

@app.route("/api/v1/recipes", methods=["POST"])
@require_auth
@rate_limit(limit=100, window=60)  # 60秒間に100リクエストまで
def create_recipe():
    # ...
```

---

## ヘルパー関数

### IPアドレス取得
```python
from backend.middleware.audit_middleware import get_client_ip

ip_address = get_client_ip(request)
```

### ユーザーID取得
```python
from flask import g

user_id = getattr(g, "user_id", None)
```

---

## カスタムログ

```python
from backend.services.audit_service import AuditAction, AuditResourceType

audit_service.log(
    action=AuditAction.RECIPE_CREATE,
    resource_type=AuditResourceType.RECIPE,
    user_id="user_001",
    resource_id="recipe_123",
    ip_address="192.168.1.100",
    details={"custom_field": "custom_value"},
    status="success"
)
```

---

## ログ分析（コマンドライン）

```bash
# 全ログ表示
cat logs/audit.json | jq '.'

# 特定ユーザー
cat logs/audit.json | jq 'select(.user_id == "user_001")'

# 認証失敗のみ
cat logs/audit.json | jq 'select(.action == "auth_failure")'

# 最近のログ（最後の10件）
tail -n 10 logs/audit.json | jq '.'

# レシピ削除のみ
cat logs/audit.json | jq 'select(.action == "recipe_delete")'

# 特定IPアドレス
cat logs/audit.json | jq 'select(.ip_address == "192.168.1.100")'

# 件数カウント
cat logs/audit.json | wc -l
```

---

## ログローテーション

```bash
# 現在のログをアーカイブ
cd logs
mv audit.json audit_$(date +%Y%m%d).json
gzip audit_*.json

# 古いログを削除（30日以上前）
find logs/ -name "audit_*.json.gz" -mtime +30 -delete
```

---

## テスト

```bash
# ユニットテスト実行
pytest backend/tests/test_audit_service.py -v

# カバレッジ
pytest backend/tests/test_audit_service.py --cov=backend/services/audit_service

# 特定テストのみ
pytest backend/tests/test_audit_service.py::TestAuditService::test_log_basic -v
```

---

## トラブルシューティング

### ログが記録されない
```bash
# 権限確認
ls -la logs/

# 書き込み権限付与
chmod 700 logs/

# ディレクトリ作成
mkdir -p logs
```

### 緊急ログ確認
```bash
cat logs/audit_emergency.json
```

### サービスログ確認
```bash
cat logs/audit_service.log
```

---

## 環境変数

```env
# .env ファイル
AUDIT_LOG_DIR=logs
AUDIT_LOG_LEVEL=INFO
```

---

## 関連ファイル

- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services/audit_service.py`
- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/middleware/audit_middleware.py`
- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/middleware/auth_with_audit.py`
- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_audit_service.py`
- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/docs/audit-logging-guide.md`
