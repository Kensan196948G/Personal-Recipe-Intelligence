# 音声アシスタント連携ドキュメント

Personal Recipe Intelligence の音声アシスタント機能に関するドキュメントです。

## 概要

Personal Recipe Intelligence は以下の音声アシスタント機能を提供します：

- **Web Speech API**: ブラウザベースの音声認識・音声合成
- **Amazon Alexa**: Alexa スキルによる音声操作
- **Google Assistant**: Google Actions による音声操作

## ディレクトリ構成

```
/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/
├── frontend/
│   ├── js/
│   │   ├── speech-service.js          # 音声認識サービス
│   │   ├── tts-service.js             # 音声合成サービス
│   │   └── voice-command-handler.js   # 音声コマンドハンドラー
│   └── components/
│       └── VoiceAssistant.jsx         # 音声アシスタントUIコンポーネント
├── alexa/
│   ├── skill.json                      # Alexa スキル定義
│   └── lambda/
│       └── index.js                    # Lambda ハンドラー
└── google-actions/
    ├── actions.json                    # Google Actions 定義
    └── webhook/
        └── index.js                    # Webhook ハンドラー
```

## Web Speech API

### speech-service.js

Web Speech API を使用した音声認識サービス。

**主な機能:**
- 日本語音声認識
- 継続的な音声認識
- 認識結果のリアルタイム取得
- エラーハンドリング

**使用例:**
```javascript
const speechService = new SpeechService();

speechService.onResult((results) => {
  results.forEach(result => {
    console.log(`Transcript: ${result.transcript}`);
    console.log(`Confidence: ${result.confidence}`);
    console.log(`Final: ${result.isFinal}`);
  });
});

speechService.onError((error) => {
  console.error(`Error: ${error.message}`);
});

speechService.start();
```

### tts-service.js

Web Speech API を使用した音声合成サービス。

**主な機能:**
- テキスト読み上げ
- レシピ全体の読み上げ
- 手順の読み上げ
- 材料リストの読み上げ
- 音量・速度・ピッチ制御

**使用例:**
```javascript
const ttsService = new TTSService();

// 基本的な読み上げ
ttsService.speak('こんにちは');

// レシピ読み上げ
ttsService.speakRecipe(recipe);

// 手順読み上げ
ttsService.speakStep(1, '玉ねぎをみじん切りにします');

// 設定変更
ttsService.setVolume(0.8);
ttsService.setRate(1.2);
```

### voice-command-handler.js

音声コマンドの解析と実行を担当。

**利用可能なコマンド:**

| コマンド | 説明 |
|---------|------|
| 次の手順 / 次 / つぎ | 次の手順へ進む |
| 前の手順 / 前 / まえ | 前の手順に戻る |
| 最初から / はじめから | 最初の手順から開始 |
| もう一度 / リピート | 現在の手順を繰り返す |
| 材料 / 材料を読んで | 材料リストを読み上げる |
| レシピ名 / タイトル | レシピ名を読み上げる |
| 全部読んで | レシピ全体を読み上げる |
| タイマー 3分 | タイマーを設定 |
| 一時停止 / ポーズ | 読み上げを一時停止 |
| 再開 / 続けて | 読み上げを再開 |
| 停止 / ストップ | 読み上げを停止 |
| 検索 カレー | レシピを検索 |
| ヘルプ / 使い方 | 使い方を表示 |

**使用例:**
```javascript
const commandHandler = new VoiceCommandHandler(speechService, ttsService);

// レシピ設定
commandHandler.setRecipe(recipe);

// コマンド実行
commandHandler.executeCommand('次の手順');

// イベントリスナー
window.addEventListener('voiceStepChange', (event) => {
  console.log(`Step changed to: ${event.detail.stepIndex}`);
});
```

### VoiceAssistant.jsx

React コンポーネントで音声アシスタントUIを提供。

**Props:**
- `recipe`: 現在のレシピオブジェクト
- `onStepChange`: 手順変更時のコールバック
- `onSearch`: 検索実行時のコールバック

**使用例:**
```jsx
import VoiceAssistant from './components/VoiceAssistant';

function RecipePage() {
  const [recipe, setRecipe] = useState(null);

  const handleStepChange = (stepIndex) => {
    console.log(`Step ${stepIndex}`);
  };

  const handleSearch = (keyword) => {
    // レシピ検索実行
  };

  return (
    <VoiceAssistant
      recipe={recipe}
      onStepChange={handleStepChange}
      onSearch={handleSearch}
    />
  );
}
```

## Amazon Alexa スキル

### セットアップ

1. **Alexa Developer Console でスキルを作成**
   - https://developer.amazon.com/alexa/console/ask
   - スキル名: "パーソナルレシピインテリジェンス"
   - 言語: 日本語

2. **skill.json をインポート**
   ```bash
   ask deploy --target skill-metadata
   ```

3. **Lambda 関数をデプロイ**
   ```bash
   cd alexa/lambda
   npm install
   zip -r function.zip .
   aws lambda create-function \
     --function-name PersonalRecipeIntelligence \
     --runtime nodejs18.x \
     --handler index.handler \
     --zip-file fileb://function.zip \
     --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role
   ```

4. **環境変数設定**
   ```bash
   aws lambda update-function-configuration \
     --function-name PersonalRecipeIntelligence \
     --environment "Variables={API_BASE_URL=https://your-api.com/api/v1}"
   ```

### 使用方法

**起動:**
```
アレクサ、パーソナルレシピを開いて
```

**コマンド例:**
- "カレーのレシピを開いて"
- "材料を読んで"
- "次の手順"
- "3分のタイマー"

## Google Assistant アクション

### セットアップ

1. **Actions Console でプロジェクト作成**
   - https://console.actions.google.com/

2. **actions.json をデプロイ**
   ```bash
   gactions push
   gactions deploy preview
   ```

3. **Webhook サーバーをデプロイ**
   ```bash
   cd google-actions/webhook
   npm install

   # Google Cloud Functions にデプロイ
   gcloud functions deploy pri-webhook \
     --runtime nodejs18 \
     --trigger-http \
     --entry-point webhook \
     --set-env-vars API_BASE_URL=https://your-api.com/api/v1
   ```

4. **Webhook URL を設定**
   - Actions Console で webhook URL を設定
   - `https://REGION-PROJECT_ID.cloudfunctions.net/pri-webhook`

### 使用方法

**起動:**
```
OK Google、パーソナルレシピと話す
```

**コマンド例:**
- "カレーのレシピ"
- "材料を教えて"
- "次の手順"
- "3分のタイマー"

## ブラウザサポート

### Web Speech API サポート状況

| ブラウザ | 音声認識 | 音声合成 |
|---------|---------|---------|
| Chrome  | ✅ | ✅ |
| Edge    | ✅ | ✅ |
| Safari  | ✅ (制限あり) | ✅ |
| Firefox | ❌ | ✅ |

**注意事項:**
- 音声認識は HTTPS 環境が必須（localhost は例外）
- Safari では連続的な音声認識に制限あり
- Firefox は音声認識に未対応

## トラブルシューティング

### 音声認識が動作しない

1. **マイク権限を確認**
   - ブラウザがマイクへのアクセスを許可しているか確認

2. **HTTPS を使用**
   - 音声認識は HTTPS 環境が必須

3. **ブラウザを確認**
   - Chrome または Edge の最新版を使用

### 音声が読み上げられない

1. **音量を確認**
   - デバイスの音量が適切か確認

2. **ブラウザ設定を確認**
   - 音声合成が有効になっているか確認

3. **音声を選択**
   - 日本語音声がインストールされているか確認

### Alexa スキルが応答しない

1. **Lambda ログを確認**
   ```bash
   aws logs tail /aws/lambda/PersonalRecipeIntelligence --follow
   ```

2. **API エンドポイントを確認**
   - Lambda 環境変数の API_BASE_URL が正しいか確認

3. **スキルを再デプロイ**
   ```bash
   ask deploy
   ```

## セキュリティ考慮事項

1. **API 認証**
   - Lambda / Webhook から API へのリクエストには認証トークンを使用

2. **HTTPS 通信**
   - すべての通信を HTTPS 経由で行う

3. **ログのマスキング**
   - 機密情報はログに出力しない

4. **レート制限**
   - API へのリクエスト数を制限

## パフォーマンス最適化

1. **レスポンスキャッシュ**
   - よく使用されるレシピをキャッシュ

2. **遅延読み込み**
   - 音声合成は必要な時のみ初期化

3. **非同期処理**
   - API リクエストは非同期で実行

## 開発・テスト

### ローカルテスト

```bash
# フロントエンド開発サーバー起動
cd frontend
bun run dev

# Alexa Lambda ローカルテスト
cd alexa/lambda
sam local start-api

# Google Webhook ローカルテスト
cd google-actions/webhook
npm run dev
```

### ユニットテスト

```bash
# フロントエンドテスト
cd frontend
bun test

# Lambda テスト
cd alexa/lambda
npm test

# Webhook テスト
cd google-actions/webhook
npm test
```

## 今後の拡張計画

- [ ] 複数言語サポート（英語、中国語）
- [ ] カスタム音声コマンドの登録
- [ ] 音声による買い物リスト作成
- [ ] 栄養情報の音声読み上げ
- [ ] 音声によるレシピ評価

## 参考リンク

- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Alexa Skills Kit](https://developer.amazon.com/alexa/alexa-skills-kit)
- [Google Actions](https://developers.google.com/assistant)

## ライセンス

本プロジェクトは MIT ライセンスの下で提供されます。
