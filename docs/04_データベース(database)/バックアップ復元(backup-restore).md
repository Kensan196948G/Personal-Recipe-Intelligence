# バックアップ・復元 (Backup & Restore)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) のデータベースバックアップと復元手順を定義する。

## 2. バックアップ戦略

### 2.1 バックアップ種別

| 種別 | 頻度 | 保持期間 | 方法 |
|------|------|----------|------|
| 日次バックアップ | 毎日 | 7日間 | 自動 |
| 週次バックアップ | 毎週日曜 | 4週間 | 自動 |
| 月次バックアップ | 毎月1日 | 12ヶ月 | 自動 |
| 手動バックアップ | 任意 | 無期限 | 手動 |

### 2.2 バックアップ対象

| 対象 | パス | 説明 |
|------|------|------|
| データベース | data/pri.db | SQLiteデータベース |
| 画像ファイル | data/images/ | レシピ画像 |
| 設定ファイル | config/ | アプリケーション設定 |

## 3. ディレクトリ構成

```
data/
├── pri.db                    # メインDB
├── images/                   # 画像ファイル
└── backups/
    ├── daily/               # 日次バックアップ
    │   ├── 2024-12-11/
    │   │   ├── pri.db
    │   │   └── images.tar.gz
    │   └── ...
    ├── weekly/              # 週次バックアップ
    ├── monthly/             # 月次バックアップ
    └── manual/              # 手動バックアップ
```

## 4. バックアップ手順

### 4.1 自動バックアップスクリプト

**scripts/backup.sh**
```bash
#!/bin/bash

# 設定
BACKUP_ROOT="/path/to/project/data/backups"
DB_PATH="/path/to/project/data/pri.db"
IMAGES_PATH="/path/to/project/data/images"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# バックアップ種別判定
DAY_OF_WEEK=$(date +%u)  # 1=月曜, 7=日曜
DAY_OF_MONTH=$(date +%d)

# 日次バックアップ
backup_daily() {
    BACKUP_DIR="$BACKUP_ROOT/daily/$DATE"
    mkdir -p "$BACKUP_DIR"

    # データベースコピー
    sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/pri.db'"

    # 画像アーカイブ
    tar -czf "$BACKUP_DIR/images.tar.gz" -C "$(dirname $IMAGES_PATH)" "$(basename $IMAGES_PATH)"

    echo "Daily backup completed: $BACKUP_DIR"
}

# 週次バックアップ（日曜日）
backup_weekly() {
    if [ "$DAY_OF_WEEK" -eq 7 ]; then
        BACKUP_DIR="$BACKUP_ROOT/weekly/$DATE"
        mkdir -p "$BACKUP_DIR"

        sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/pri.db'"
        tar -czf "$BACKUP_DIR/images.tar.gz" -C "$(dirname $IMAGES_PATH)" "$(basename $IMAGES_PATH)"

        echo "Weekly backup completed: $BACKUP_DIR"
    fi
}

# 月次バックアップ（1日）
backup_monthly() {
    if [ "$DAY_OF_MONTH" -eq "01" ]; then
        BACKUP_DIR="$BACKUP_ROOT/monthly/$DATE"
        mkdir -p "$BACKUP_DIR"

        sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/pri.db'"
        tar -czf "$BACKUP_DIR/images.tar.gz" -C "$(dirname $IMAGES_PATH)" "$(basename $IMAGES_PATH)"

        echo "Monthly backup completed: $BACKUP_DIR"
    fi
}

# 古いバックアップ削除
cleanup_old_backups() {
    # 7日以上前の日次バックアップを削除
    find "$BACKUP_ROOT/daily" -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null

    # 4週間以上前の週次バックアップを削除
    find "$BACKUP_ROOT/weekly" -type d -mtime +28 -exec rm -rf {} \; 2>/dev/null

    # 12ヶ月以上前の月次バックアップを削除
    find "$BACKUP_ROOT/monthly" -type d -mtime +365 -exec rm -rf {} \; 2>/dev/null

    echo "Old backups cleaned up"
}

# 実行
backup_daily
backup_weekly
backup_monthly
cleanup_old_backups

echo "Backup process completed at $(date)"
```

### 4.2 手動バックアップ

```bash
# 手動バックアップスクリプト
#!/bin/bash

BACKUP_ROOT="/path/to/project/data/backups/manual"
DB_PATH="/path/to/project/data/pri.db"
IMAGES_PATH="/path/to/project/data/images"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"

mkdir -p "$BACKUP_DIR"

# データベースバックアップ
sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/pri.db'"

# 画像バックアップ
tar -czf "$BACKUP_DIR/images.tar.gz" -C "$(dirname $IMAGES_PATH)" "$(basename $IMAGES_PATH)"

# バックアップ情報
echo "Backup created at: $(date)" > "$BACKUP_DIR/backup_info.txt"
echo "Database size: $(du -h "$BACKUP_DIR/pri.db" | cut -f1)" >> "$BACKUP_DIR/backup_info.txt"
echo "Images size: $(du -h "$BACKUP_DIR/images.tar.gz" | cut -f1)" >> "$BACKUP_DIR/backup_info.txt"

echo "Manual backup completed: $BACKUP_DIR"
```

### 4.3 cron設定

```bash
# crontab -e
# 毎日午前3時に日次バックアップ
0 3 * * * /path/to/project/scripts/backup.sh >> /path/to/project/logs/backup.log 2>&1
```

## 5. 復元手順

### 5.1 データベース復元

```bash
#!/bin/bash

# 復元スクリプト
BACKUP_PATH="$1"  # バックアップディレクトリ
DB_PATH="/path/to/project/data/pri.db"
IMAGES_PATH="/path/to/project/data/images"

if [ -z "$BACKUP_PATH" ]; then
    echo "Usage: restore.sh <backup_directory>"
    exit 1
fi

# アプリケーション停止
echo "Stopping application..."
# pkill -f "uvicorn"  # 必要に応じてコメント解除

# 現在のデータをバックアップ
TEMP_BACKUP="/tmp/pri_restore_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$TEMP_BACKUP"
cp "$DB_PATH" "$TEMP_BACKUP/"
cp -r "$IMAGES_PATH" "$TEMP_BACKUP/"
echo "Current data backed up to: $TEMP_BACKUP"

# データベース復元
if [ -f "$BACKUP_PATH/pri.db" ]; then
    cp "$BACKUP_PATH/pri.db" "$DB_PATH"
    echo "Database restored"
else
    echo "Error: Database backup not found"
    exit 1
fi

# 画像復元
if [ -f "$BACKUP_PATH/images.tar.gz" ]; then
    rm -rf "$IMAGES_PATH"
    tar -xzf "$BACKUP_PATH/images.tar.gz" -C "$(dirname $IMAGES_PATH)"
    echo "Images restored"
fi

# アプリケーション起動
echo "Starting application..."
# uvicorn backend.api.main:app --reload &  # 必要に応じてコメント解除

echo "Restore completed from: $BACKUP_PATH"
```

### 5.2 特定テーブルの復元

```bash
# 特定テーブルのみ復元
sqlite3 backup/pri.db ".dump recipe" | sqlite3 data/pri.db
```

### 5.3 部分復元（特定レシピ）

```sql
-- バックアップDBをアタッチ
ATTACH DATABASE 'backup/pri.db' AS backup;

-- 特定レシピを復元
INSERT INTO recipe SELECT * FROM backup.recipe WHERE id = 123;
INSERT INTO recipe_ingredient SELECT * FROM backup.recipe_ingredient WHERE recipe_id = 123;
INSERT INTO recipe_step SELECT * FROM backup.recipe_step WHERE recipe_id = 123;
INSERT INTO recipe_tag SELECT * FROM backup.recipe_tag WHERE recipe_id = 123;

DETACH DATABASE backup;
```

## 6. バックアップ検証

### 6.1 整合性チェック

```bash
# SQLiteの整合性チェック
sqlite3 data/backups/daily/2024-12-11/pri.db "PRAGMA integrity_check;"
```

### 6.2 復元テスト

```bash
# 一時DBに復元してテスト
sqlite3 /tmp/test_restore.db < backup.sql
sqlite3 /tmp/test_restore.db "SELECT COUNT(*) FROM recipe;"
rm /tmp/test_restore.db
```

## 7. 監視・通知

### 7.1 バックアップ監視スクリプト

```bash
#!/bin/bash

BACKUP_ROOT="/path/to/project/data/backups"
LOG_FILE="/path/to/project/logs/backup_monitor.log"

# 最新バックアップの確認
LATEST_DAILY=$(ls -t "$BACKUP_ROOT/daily" | head -1)
LATEST_DATE=$(date -d "$LATEST_DAILY" +%s 2>/dev/null)
CURRENT_DATE=$(date +%s)
DIFF=$((($CURRENT_DATE - $LATEST_DATE) / 86400))

if [ $DIFF -gt 1 ]; then
    echo "[$(date)] WARNING: Daily backup is $DIFF days old" >> "$LOG_FILE"
fi

# バックアップサイズの確認
BACKUP_SIZE=$(du -sh "$BACKUP_ROOT/daily/$LATEST_DAILY" 2>/dev/null | cut -f1)
echo "[$(date)] Latest backup: $LATEST_DAILY, Size: $BACKUP_SIZE" >> "$LOG_FILE"
```

## 8. トラブルシューティング

### 8.1 バックアップ失敗時

1. ディスク空き容量を確認
2. パーミッションを確認
3. SQLiteのロック状態を確認

### 8.2 復元失敗時

1. バックアップファイルの整合性を確認
2. 外部キー制約を一時的に無効化
3. 手動でデータを移行

```sql
-- 外部キー制約を無効化
PRAGMA foreign_keys = OFF;
-- ... 復元処理 ...
PRAGMA foreign_keys = ON;
```

## 9. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |
