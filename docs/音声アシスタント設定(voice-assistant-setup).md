# 音声アシスタント機能セットアップガイド

## クイックスタート

### 1. 依存関係インストール

```bash
# バックエンド
cd backend
pip install -r requirements.txt

# フロントエンド
cd frontend
bun install
```

### 2. データディレクトリ作成

```bash
mkdir -p data/voice
```

### 3. バックエンド起動

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 4. フロントエンド起動

```bash
cd frontend
bun run dev
```

### 5. ブラウザでアクセス

```
http://localhost:3000/voice-demo
```

## テスト実行

### ユニットテスト

```bash
cd backend
pytest tests/test_voice_assistant_service.py -v
```

### カバレッジ付き

```bash
pytest tests/test_voice_assistant_service.py --cov=services.voice_assistant_service --cov-report=html
```

### 統合テスト

```bash
# Alexa リクエストテスト
curl -X POST http://localhost:8001/api/v1/voice/alexa \
  -H "Content-Type: application/json" \
  -d @backend/tests/fixtures/alexa_request.json

# Google リクエストテスト
curl -X POST http://localhost:8001/api/v1/voice/google \
  -H "Content-Type: application/json" \
  -d @backend/tests/fixtures/google_request.json

# 汎用コマンドテスト
curl -X POST http://localhost:8001/api/v1/voice/generic \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "command": "カレーのレシピ",
    "language": "ja-JP"
  }'
```

## API エンドポイント確認

### ヘルスチェック

```bash
curl http://localhost:8001/api/v1/voice/health
```

### 対応インテント一覧

```bash
curl http://localhost:8001/api/v1/voice/intents | jq
```

### セッション一覧

```bash
curl http://localhost:8001/api/v1/voice/sessions | jq
```

## ブラウザ音声認識テスト

1. `http://localhost:3000/voice-demo` にアクセス
2. マイクボタンをクリック
3. ブラウザのマイク許可を承認
4. 以下のコマンドを試す：
   - 「カレーのレシピ」
   - 「次」
   - 「材料」
   - 「タイマー5分」

## トラブルシューティング

### 音声認識が動作しない

**問題**: マイクボタンをクリックしても反応しない

**原因**: ブラウザがWeb Speech APIに対応していない、またはHTTPS環境でない

**解決策**:
- Chrome, Edge, Safari の最新版を使用
- ローカル開発は `localhost` でアクセス（HTTPでも動作）
- 本番環境ではHTTPSを使用

### マイク許可が表示されない

**問題**: マイク許可のダイアログが出ない

**解決策**:
- ブラウザの設定からマイク許可を確認
- Chrome: `chrome://settings/content/microphone`
- プライベートブラウジングモードでは動作しない場合がある

### APIエラーが発生する

**問題**: `Failed to fetch` エラー

**解決策**:
- バックエンドが起動しているか確認
- CORS設定を確認
- ネットワークタブでリクエストを確認

```bash
# バックエンドログ確認
tail -f logs/app.log
```

### セッションが保存されない

**問題**: セッション情報が永続化されない

**解決策**:
- `data/voice/` ディレクトリの書き込み権限を確認
- ディスク容量を確認

```bash
ls -la data/voice/
cat data/voice/sessions.json | jq
```

## デバッグモード

### ログレベル変更

```python
# backend/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 詳細ログ出力

```bash
# 環境変数設定
export LOG_LEVEL=DEBUG
python -m uvicorn main:app --reload
```

## パフォーマンス確認

### レスポンスタイム計測

```bash
curl -w "@curl-format.txt" -o /dev/null -s \
  http://localhost:8001/api/v1/voice/generic \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "command": "カレーのレシピ"}'
```

curl-format.txt:
```
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_appconnect:  %{time_appconnect}\n
time_pretransfer:  %{time_pretransfer}\n
time_redirect:  %{time_redirect}\n
time_starttransfer:  %{time_starttransfer}\n
----------\n
time_total:  %{time_total}\n
```

## プロダクション設定

### HTTPS設定

```bash
# Let's Encrypt 証明書取得
certbot certonly --standalone -d your-domain.com
```

### Nginx設定例

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location /api/v1/voice/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 環境変数

```bash
# .env
VOICE_DATA_DIR=data/voice
VOICE_SESSION_MAX_AGE_HOURS=24
VOICE_MAX_SESSIONS=1000
```

## 監視とメンテナンス

### セッションクリーンアップ（Cron設定）

```bash
# 毎日午前3時に実行
0 3 * * * curl -X POST http://localhost:8001/api/v1/voice/sessions/cleanup
```

### ログローテーション

```bash
# /etc/logrotate.d/pri-voice
/path/to/logs/voice_assistant.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

## 参考資料

- [音声アシスタント統合ガイド](./voice-assistant-integration.md)
- [API仕様書](./api-specification.md)
- [Web Speech API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
