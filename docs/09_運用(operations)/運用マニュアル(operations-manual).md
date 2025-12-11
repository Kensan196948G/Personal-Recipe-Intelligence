# 運用マニュアル (Operations Manual)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) の運用手順を定義する。

## 2. システム起動・停止

### 2.1 起動手順

```bash
# 1. プロジェクトディレクトリに移動
cd /path/to/personal-recipe-intelligence

# 2. 環境変数確認
cat .env

# 3. バックエンド起動
cd backend
source venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# 4. フロントエンド起動
cd ../frontend
bun run dev &

# または一括起動
./scripts/dev.sh
```

### 2.2 停止手順

```bash
# プロセス確認
ps aux | grep uvicorn
ps aux | grep vite

# プロセス終了
kill <PID>

# または
pkill -f uvicorn
pkill -f vite
```

### 2.3 再起動

```bash
# サービス再起動
./scripts/restart.sh
```

## 3. ログ管理

### 3.1 ログ場所

| ログ種別 | パス |
|---------|------|
| アプリケーション | logs/app.log |
| アクセスログ | logs/access.log |
| エラーログ | logs/error.log |

### 3.2 ログ確認

```bash
# リアルタイム監視
tail -f logs/app.log

# エラー検索
grep "ERROR" logs/app.log

# 特定日付のログ
grep "2024-12-11" logs/app.log
```

### 3.3 ログローテーション

```bash
# logrotate設定
sudo cat > /etc/logrotate.d/pri << EOF
/path/to/project/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 user group
}
EOF
```

## 4. バックアップ

### 4.1 手動バックアップ

```bash
# データベースバックアップ
sqlite3 data/pri.db ".backup data/backups/manual/pri_$(date +%Y%m%d_%H%M%S).db"

# 画像バックアップ
tar -czf data/backups/manual/images_$(date +%Y%m%d).tar.gz data/images/

# 設定バックアップ
cp .env data/backups/manual/env_$(date +%Y%m%d).bak
```

### 4.2 自動バックアップ

```bash
# cron設定
crontab -e

# 毎日午前3時にバックアップ
0 3 * * * /path/to/project/scripts/backup.sh >> /path/to/project/logs/backup.log 2>&1
```

### 4.3 復元

```bash
# データベース復元
cp data/backups/daily/2024-12-11/pri.db data/pri.db

# 画像復元
tar -xzf data/backups/daily/2024-12-11/images.tar.gz -C data/
```

## 5. 監視

### 5.1 ヘルスチェック

```bash
# APIヘルスチェック
curl http://localhost:8000/health

# レスポンス例
{"status": "ok"}
```

### 5.2 ディスク使用量

```bash
# 全体
df -h

# プロジェクトディレクトリ
du -sh /path/to/project/*
```

### 5.3 プロセス監視

```bash
# CPU/メモリ使用量
top -p $(pgrep -f uvicorn)

# プロセス状態
ps aux | grep -E "(uvicorn|vite)"
```

## 6. メンテナンス

### 6.1 データベースメンテナンス

```bash
# 最適化
sqlite3 data/pri.db "VACUUM;"

# 整合性チェック
sqlite3 data/pri.db "PRAGMA integrity_check;"

# 統計更新
sqlite3 data/pri.db "ANALYZE;"
```

### 6.2 ログクリーンアップ

```bash
# 30日以上前のログ削除
find logs/ -name "*.log" -mtime +30 -delete
```

### 6.3 キャッシュクリア

```bash
# Python キャッシュ
find . -type d -name "__pycache__" -exec rm -rf {} +

# bun キャッシュ
cd frontend && rm -rf node_modules/.cache
```

## 7. 障害対応

### 7.1 障害切り分け

1. **ログ確認**
   ```bash
   tail -100 logs/error.log
   ```

2. **プロセス確認**
   ```bash
   ps aux | grep -E "(uvicorn|vite)"
   ```

3. **ネットワーク確認**
   ```bash
   curl -v http://localhost:8000/health
   ```

4. **ディスク確認**
   ```bash
   df -h
   ```

### 7.2 よくある問題と対処

| 問題 | 原因 | 対処 |
|------|------|------|
| API応答なし | プロセス停止 | 再起動 |
| DB接続エラー | ファイル破損 | バックアップ復元 |
| ディスクフル | ログ肥大化 | ログクリーンアップ |
| メモリ不足 | リーク | プロセス再起動 |

### 7.3 エスカレーション

1. 自己解決を試みる
2. ログを保存
3. 問題を記録

## 8. 定期作業

### 8.1 日次

- [ ] ログ確認
- [ ] バックアップ確認
- [ ] ディスク使用量確認

### 8.2 週次

- [ ] 週次バックアップ確認
- [ ] パフォーマンス確認
- [ ] エラー傾向分析

### 8.3 月次

- [ ] 月次バックアップ確認
- [ ] 依存関係更新検討
- [ ] ディスククリーンアップ

## 9. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |
