# バックアップ API 使用ガイド

Personal Recipe Intelligence の SQLite データベースバックアップ機能の使用方法を説明します。

## 概要

バックアップ機能は以下の機能を提供します：

- SQLite データベースの手動/自動バックアップ
- バックアップファイルの gzip 圧縮
- 世代管理（最大 N 世代保持）
- バックアップからのリストア
- バックアップ状態の確認

## API エンドポイント

### 1. バックアップ作成

**POST** `/api/v1/backup/create`

手動でバックアップを作成します。

#### リクエスト

```json
{
  "backup_name": "manual_backup"
}
```

- `backup_name` (optional): バックアップファイル名（省略時はタイムスタンプを使用）

#### レスポンス

```json
{
  "status": "ok",
  "data": {
    "backup_id": "backup_20251211_143025.db.gz",
    "filename": "backup_20251211_143025.db.gz",
    "filepath": "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/data/backups/backup_20251211_143025.db.gz",
    "size_bytes": 4096,
    "size_mb": 0.00390625,
    "created_at": "2025-12-11T14:30:25",
    "is_compressed": true
  },
  "error": null
}
```

#### cURL 例

```bash
# デフォルト名でバックアップ作成
curl -X POST http://localhost:8000/api/v1/backup/create \
  -H "Content-Type: application/json" \
  -d '{}'

# カスタム名でバックアップ作成
curl -X POST http://localhost:8000/api/v1/backup/create \
  -H "Content-Type: application/json" \
  -d '{"backup_name": "before_update"}'
```

---

### 2. バックアップ一覧取得

**GET** `/api/v1/backup/list`

全バックアップの一覧を取得します（作成日時の降順）。

#### レスポンス

```json
{
  "status": "ok",
  "data": [
    {
      "backup_id": "backup_20251211_143025.db.gz",
      "filename": "backup_20251211_143025.db.gz",
      "filepath": "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/data/backups/backup_20251211_143025.db.gz",
      "size_bytes": 4096,
      "size_mb": 0.00390625,
      "created_at": "2025-12-11T14:30:25",
      "is_compressed": true
    },
    {
      "backup_id": "backup_20251211_120000.db.gz",
      "filename": "backup_20251211_120000.db.gz",
      "filepath": "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/data/backups/backup_20251211_120000.db.gz",
      "size_bytes": 4096,
      "size_mb": 0.00390625,
      "created_at": "2025-12-11T12:00:00",
      "is_compressed": true
    }
  ],
  "error": null
}
```

#### cURL 例

```bash
curl -X GET http://localhost:8000/api/v1/backup/list
```

---

### 3. バックアップからリストア

**POST** `/api/v1/backup/restore/{backup_id}`

指定したバックアップからデータベースをリストアします。

**注意**: リストア実行前に現在のデータベースの安全バックアップが自動作成されます。

#### パラメータ

- `backup_id`: リストアするバックアップのID（ファイル名）

#### レスポンス

```json
{
  "status": "ok",
  "data": {
    "backup_id": "backup_20251211_120000.db.gz",
    "restored": true,
    "message": "Restore completed successfully"
  },
  "error": null
}
```

#### cURL 例

```bash
curl -X POST http://localhost:8000/api/v1/backup/restore/backup_20251211_120000.db.gz
```

---

### 4. バックアップ削除

**DELETE** `/api/v1/backup/{backup_id}`

指定したバックアップを削除します。

#### パラメータ

- `backup_id`: 削除するバックアップのID（ファイル名）

#### レスポンス

```json
{
  "status": "ok",
  "data": {
    "backup_id": "backup_20251211_120000.db.gz",
    "deleted": true,
    "message": "Backup deleted successfully"
  },
  "error": null
}
```

#### cURL 例

```bash
curl -X DELETE http://localhost:8000/api/v1/backup/backup_20251211_120000.db.gz
```

---

### 5. バックアップ状態確認

**GET** `/api/v1/backup/status`

バックアップの全体的な状態を取得します。

#### レスポンス

```json
{
  "status": "ok",
  "data": {
    "total_backups": 5,
    "total_size_mb": 0.02,
    "oldest_backup": "2025-12-10T10:00:00",
    "latest_backup": "2025-12-11T14:30:25",
    "backup_dir": "/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/data/backups"
  },
  "error": null
}
```

#### cURL 例

```bash
curl -X GET http://localhost:8000/api/v1/backup/status
```

---

## Python サービス直接利用

API を経由せずに Python コードから直接利用することも可能です。

```python
from backend.services.backup_service import BackupService

# サービスの初期化
backup_service = BackupService(
    db_path="data/recipes.db",
    backup_dir="data/backups",
    max_generations=10,
    compress=True
)

# バックアップ作成
backup_info = backup_service.create_backup()
print(f"Created backup: {backup_info.backup_id}")

# バックアップ一覧取得
backups = backup_service.list_backups()
for backup in backups:
    print(f"- {backup.filename} ({backup.size_mb} MB)")

# リストア
backup_service.restore_backup("backup_20251211_120000.db.gz")

# 削除
backup_service.delete_backup("backup_20251211_120000.db.gz")

# 状態確認
status = backup_service.get_status()
print(f"Total backups: {status.total_backups}")
```

---

## 世代管理

バックアップは自動的に世代管理されます：

- デフォルトで最大 **10 世代** を保持
- 新しいバックアップ作成時、古いバックアップが自動削除される
- `max_generations` パラメータで変更可能

---

## セキュリティ

- バックアップファイルは `data/backups/` ディレクトリに保存
- リストア実行前に安全バックアップが自動作成される
- 削除操作は元に戻せないため注意が必要

---

## エラーハンドリング

### 404 Not Found

バックアップファイルが存在しない場合：

```json
{
  "detail": "Backup file not found: backup_20251211_120000.db.gz"
}
```

### 500 Internal Server Error

バックアップ作成/リストア/削除に失敗した場合：

```json
{
  "detail": "Failed to create backup: Permission denied"
}
```

---

## テスト

バックアップ機能のテストを実行：

```bash
pytest tests/test_backup_service.py -v
```

---

## スケジュール設定（将来実装）

現在は手動バックアップのみですが、将来的には以下の機能を追加予定：

- cron による定期バックアップ
- イベント駆動バックアップ（データ更新時など）
- バックアップスケジュール設定 API
