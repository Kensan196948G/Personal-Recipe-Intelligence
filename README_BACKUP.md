# Backend Services - Backup

Personal Recipe Intelligence のバックエンドサービス層です。

## サービス一覧

### BackupService (`backup_service.py`)

SQLite データベースの自動バックアップ・リストア機能を提供します。

#### 主な機能

- データベースの手動/自動バックアップ
- gzip 圧縮によるストレージ節約
- 世代管理（古いバックアップの自動削除）
- バックアップからのリストア（安全バックアップ付き）
- バックアップ状態の確認

#### 使用例

```python
from backend.services.backup_service import BackupService

# サービスの初期化
service = BackupService(
    db_path="data/recipes.db",
    backup_dir="data/backups",
    max_generations=10,
    compress=True
)

# バックアップ作成
backup_info = service.create_backup()
print(f"Created: {backup_info.backup_id}")

# バックアップ一覧
backups = service.list_backups()
for backup in backups:
    print(f"- {backup.filename} ({backup.size_mb} MB)")

# リストア
service.restore_backup(backup_info.backup_id)

# 削除
service.delete_backup(backup_info.backup_id)

# 状態確認
status = service.get_status()
print(f"Total: {status.total_backups} backups, {status.total_size_mb} MB")
```

#### API エンドポイント

バックアップサービスは REST API としても利用可能です。

詳細は `/docs/backup-api-usage.md` を参照してください。

- `POST /api/v1/backup/create` - バックアップ作成
- `GET /api/v1/backup/list` - バックアップ一覧
- `POST /api/v1/backup/restore/{backup_id}` - リストア
- `DELETE /api/v1/backup/{backup_id}` - 削除
- `GET /api/v1/backup/status` - 状態確認

#### CLI ツール

シェルスクリプトからも利用可能です：

```bash
# バックアップ作成
./scripts/backup.sh create

# バックアップ一覧
./scripts/backup.sh list

# リストア
./scripts/backup.sh restore backup_20251211_143025.db.gz

# 削除
./scripts/backup.sh delete backup_20251211_143025.db.gz

# 状態確認
./scripts/backup.sh status
```

#### テスト

```bash
pytest tests/test_backup_service.py -v
```

---

## ディレクトリ構成

```
backend/
├── services/
│   ├── backup_service.py      # バックアップサービス
│   └── README.md              # 本ファイル
├── api/
│   └── routers/
│       └── backup.py          # バックアップAPI
└── ...
```

---

## 設定

バックアップサービスの設定は `config/backup_config.example.py` を参照してください。

主な設定項目：

- `DATABASE_PATH`: バックアップ対象のデータベースパス
- `BACKUP_DIR`: バックアップファイル保存先
- `MAX_BACKUP_GENERATIONS`: 保持する最大世代数
- `ENABLE_COMPRESSION`: gzip圧縮の有効/無効

---

## 今後の拡張予定

- 定期自動バックアップ（cron連携）
- イベント駆動バックアップ（データ更新時など）
- バックアップのクラウド保存（S3等）
- 増分バックアップ
- バックアップの暗号化
