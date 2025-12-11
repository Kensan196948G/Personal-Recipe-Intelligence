# 音声アシスタント連携ガイド

Personal Recipe Intelligence の音声アシスタント機能の統合ガイドです。

## 概要

本システムは以下の音声アシスタントプラットフォームに対応しています：

- **Webブラウザ（Web Speech API）**
- **Amazon Alexa（Alexa Skills Kit）**
- **Google Assistant（Conversational Actions）**

## 1. Webブラウザでの利用

### 対応ブラウザ

- Google Chrome 25+
- Microsoft Edge 79+
- Safari 14.1+
- Firefox 非対応（Web Speech API未実装）

### 使い方

1. `/voice-demo` ページにアクセス
2. マイクボタンをクリック
3. ブラウザのマイク許可ダイアログで「許可」を選択
4. 音声コマンドを話す

### 技術仕様

- **API**: Web Speech API（SpeechRecognition）
- **言語**: ja-JP（日本語）
- **通信**: REST API（`/api/v1/voice/generic`）
- **セッション管理**: ブラウザローカル + サーバー側JSON

## 2. Amazon Alexa連携

### 前提条件

- Amazon Developer アカウント
- Alexa Skills Kit（ASK）の基本知識
- HTTPS エンドポイント（SSL証明書必須）

### セットアップ手順

#### 2.1 Alexa Skillの作成

1. [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask) にログイン
2. 「スキルの作成」をクリック
3. スキル名を入力（例：「レシピアシスタント」）
4. デフォルト言語: 日本語
5. スキルモデル: カスタム
6. ホスティング方法: 自分でプロビジョニング

#### 2.2 インタラクションモデルの構築

`config/alexa/interaction-model.json` を使用してインテントを設定：

```json
{
  "interactionModel": {
    "languageModel": {
      "invocationName": "レシピアシスタント",
      "intents": [
        {
          "name": "SearchRecipe",
          "slots": [
            {
              "name": "query",
              "type": "AMAZON.SearchQuery"
            }
          ],
          "samples": [
            "{query}のレシピ",
            "{query}の作り方",
            "{query}を作りたい"
          ]
        },
        {
          "name": "NextStep",
          "samples": [
            "次",
            "次の手順",
            "次へ"
          ]
        },
        {
          "name": "PreviousStep",
          "samples": [
            "前",
            "前の手順",
            "戻る"
          ]
        }
      ]
    }
  }
}
```

#### 2.3 エンドポイント設定

1. 「エンドポイント」タブを開く
2. サービスエンドポイントタイプ: HTTPS
3. デフォルトリージョン: `https://your-domain.com/api/v1/voice/alexa`
4. SSL証明書タイプ: サブドメインのワイルドカード証明書

#### 2.4 スキルのテスト

1. 「テスト」タブを開く
2. テストを有効化
3. 「レシピアシスタントを開いて」と入力
4. スキルが起動することを確認

### リクエスト形式

```json
{
  "version": "1.0",
  "session": {
    "sessionId": "SessionId.xxx",
    "application": {
      "applicationId": "amzn1.ask.skill.xxx"
    }
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "EdwRequestId.xxx",
    "intent": {
      "name": "SearchRecipe",
      "slots": {
        "query": {
          "name": "query",
          "value": "カレー"
        }
      }
    }
  }
}
```

### レスポンス形式

```json
{
  "version": "1.0",
  "response": {
    "outputSpeech": {
      "type": "SSML",
      "ssml": "<speak>カレーのレシピを検索しています</speak>"
    },
    "shouldEndSession": false
  }
}
```

## 3. Google Assistant連携

### 前提条件

- Google Cloud Platform アカウント
- Actions on Google プロジェクト
- HTTPS エンドポイント

### セットアップ手順

#### 3.1 Actions on Google プロジェクト作成

1. [Actions Console](https://console.actions.google.com/) にアクセス
2. 「新しいプロジェクト」をクリック
3. プロジェクト名を入力
4. 言語: 日本語

#### 3.2 Conversational Action の構築

1. アクションタイプ: Custom
2. Webhook URL: `https://your-domain.com/api/v1/voice/google`
3. インテントを追加：
   - SearchRecipe
   - NextStep
   - PreviousStep
   - GetIngredients
   - SetTimer

#### 3.3 インテントの設定

```yaml
intents:
  SearchRecipe:
    training_phrases:
      - カレーのレシピ
      - パスタの作り方
      - $query のレシピを教えて
    parameters:
      - name: query
        type: schema.org/Text

  NextStep:
    training_phrases:
      - 次
      - 次の手順
      - 次へ進んで
```

### リクエスト形式

```json
{
  "handler": {
    "name": "SearchRecipe"
  },
  "intent": {
    "name": "SearchRecipe",
    "params": {
      "query": {
        "original": "カレー",
        "resolved": "カレー"
      }
    }
  },
  "session": {
    "id": "xxx",
    "params": {}
  }
}
```

### レスポンス形式

```json
{
  "session": {
    "params": {}
  },
  "prompt": {
    "override": false,
    "content": {
      "speech": "<speak>カレーのレシピを検索しています</speak>"
    }
  }
}
```

## 4. 対応インテント一覧

| インテント | 説明 | パラメータ | サンプルフレーズ |
|-----------|------|----------|----------------|
| SearchRecipe | レシピ検索 | query | 「カレーのレシピ」 |
| GetRecipeSteps | レシピ手順取得 | recipe_id | 「作り方を教えて」 |
| GetIngredients | 材料リスト取得 | - | 「材料は何？」 |
| NextStep | 次の手順 | - | 「次」 |
| PreviousStep | 前の手順 | - | 「前」 |
| RepeatStep | 手順繰り返し | - | 「もう一度」 |
| SetTimer | タイマー設定 | duration | 「タイマー5分」 |
| Help | ヘルプ | - | 「ヘルプ」 |
| Cancel | キャンセル | - | 「キャンセル」 |

## 5. SSML（音声合成マークアップ）

### 基本構文

```xml
<speak>
  こんにちは。
  <break time="500ms"/>
  レシピアシスタントです。
</speak>
```

### サポートされるタグ

- `<speak>`: ルート要素
- `<break time="Xms">`: 一時停止
- `<emphasis level="strong">`: 強調
- `<prosody rate="slow">`: 速度調整
- `<say-as interpret-as="number">`: 数値読み上げ

### 使用例

```xml
<speak>
  手順<say-as interpret-as="ordinal">1</say-as>:
  <break time="300ms"/>
  玉ねぎを<emphasis level="strong">薄く</emphasis>切ります。
  <break time="500ms"/>
  次の手順を聞くには「次」と言ってください。
</speak>
```

## 6. セッション管理

### セッションライフサイクル

1. **作成**: 初回リクエスト時に自動生成
2. **更新**: 各リクエストで `last_access` を更新
3. **削除**: 24時間非アクティブで自動削除

### セッションデータ構造

```json
{
  "session_id": "session_xxx",
  "created_at": "2025-12-11T10:00:00",
  "last_access": "2025-12-11T10:15:00",
  "current_recipe_id": "recipe_001",
  "current_step_index": 2,
  "context": {
    "steps": ["手順1", "手順2", "手順3"],
    "last_search": "カレー"
  }
}
```

### API エンドポイント

```bash
# セッション一覧取得
GET /api/v1/voice/sessions

# 特定セッション削除
DELETE /api/v1/voice/sessions/{session_id}

# 古いセッションクリーンアップ
POST /api/v1/voice/sessions/cleanup
```

## 7. セキュリティ

### Alexa リクエスト署名検証

本番環境では必ず実装してください：

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509 import load_pem_x509_certificate

def verify_alexa_signature(signature, cert_url, request_body):
    # 証明書取得
    cert = get_certificate(cert_url)

    # 署名検証
    public_key = cert.public_key()
    public_key.verify(
        signature,
        request_body,
        padding.PKCS1v15(),
        hashes.SHA1()
    )
```

### Google Actions 検証

Actions Console で提供される JWT トークンを検証：

```python
from google.auth.transport import requests
from google.oauth2 import id_token

def verify_google_token(token):
    idinfo = id_token.verify_oauth2_token(
        token,
        requests.Request(),
        audience='your-project-id'
    )
    return idinfo
```

## 8. トラブルシューティング

### よくある問題

#### 音声認識が動作しない（ブラウザ）

- **原因**: HTTPS環境でない
- **解決**: ローカル開発は `localhost` を使用（HTTPでも動作）

#### Alexa Skillが応答しない

- **原因**: エンドポイントURLが間違っている
- **解決**: CloudWatch Logs でエラー確認

#### Google Actionがタイムアウトする

- **原因**: レスポンスが5秒以内に返っていない
- **解決**: 処理の最適化、非同期処理の活用

### ログ確認

```bash
# バックエンドログ
tail -f logs/voice_assistant.log

# セッションデータ
cat data/voice/sessions.json | jq
```

## 9. テスト方法

### ユニットテスト

```bash
cd backend
pytest tests/test_voice_assistant_service.py -v
```

### 統合テスト

```bash
# Alexa リクエストシミュレーション
curl -X POST http://localhost:8000/api/v1/voice/alexa \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/alexa_request.json

# Google リクエストシミュレーション
curl -X POST http://localhost:8000/api/v1/voice/google \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/google_request.json
```

### 手動テスト

1. Alexa Developer Console の「テスト」タブ
2. Google Actions Console の「Simulator」
3. ブラウザの `/voice-demo` ページ

## 10. パフォーマンス最適化

### キャッシング

レシピデータは事前にキャッシュしてレスポンス時間を短縮：

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_recipe(recipe_id: str):
    # レシピ取得処理
    pass
```

### 非同期処理

タイマー設定などの長時間処理は非同期化：

```python
import asyncio

async def set_timer(duration: int):
    await asyncio.sleep(duration * 60)
    # 通知送信
    pass
```

## 11. 今後の拡張

- [ ] Apple Siri ショートカット対応
- [ ] LINE Clova 連携
- [ ] 多言語対応（英語、中国語など）
- [ ] プッシュ通知（タイマー完了時）
- [ ] レシピ画像の音声説明
- [ ] 音声での評価・レビュー投稿

## 参考リンク

- [Alexa Skills Kit Documentation](https://developer.amazon.com/docs/ask-overviews/what-is-the-alexa-skills-kit.html)
- [Actions on Google Documentation](https://developers.google.com/assistant)
- [Web Speech API Specification](https://w3c.github.io/speech-api/)
- [SSML Reference](https://www.w3.org/TR/speech-synthesis/)
