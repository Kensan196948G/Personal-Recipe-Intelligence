# Phase 12-2: 食材画像認識機能 実装ドキュメント

## 概要
画像から食材を識別する機能を実装。カメラ撮影・ファイルアップロードに対応し、認識結果からレシピ検索が可能。

## 実装ファイル

### 1. バックエンドサービス

#### `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/services/image_recognition_service.py`
- **ImageRecognitionService クラス**
  - 画像認識のコアロジック
  - モックモード（デモ用）と本番モード対応
  - 100種類の日本の一般的な食材辞書
  - 画像前処理（リサイズ、最適化）
  - キャッシュ機能（24時間有効）
  - Base64エンコード対応

- **主要メソッド**
  - `recognize_from_file()` - ファイルパスから認識
  - `recognize_from_base64()` - Base64画像から認識
  - `recognize_from_url()` - URL画像から認識
  - `get_ingredient_info()` - 食材詳細情報取得
  - `search_ingredients()` - 食材検索
  - `get_categories()` - カテゴリ一覧取得

- **食材辞書**
  - 野菜: 30種類
  - 肉類: 7種類
  - 魚介類: 10種類
  - 卵・乳製品: 5種類
  - 穀物・麺類: 7種類
  - 豆類: 4種類
  - 調味料: 10種類
  - 果物: 10種類
  - その他: 20種類以上
  - 合計: 100種類以上

### 2. APIルーター

#### `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/api/routers/image_recognition.py`
- **エンドポイント**

1. **POST /api/v1/ai/image/recognize**
   - Base64画像から食材認識
   - リクエスト: `{ image_base64: string, max_results: int }`
   - レスポンス: 認識結果リスト

2. **POST /api/v1/ai/image/recognize-file**
   - ファイルアップロードから認識
   - リクエスト: multipart/form-data
   - レスポンス: 認識結果リスト

3. **POST /api/v1/ai/image/recognize-url**
   - URL画像から認識（モックモード時はダミー）
   - リクエスト: `{ image_url: string, max_results: int }`
   - レスポンス: 認識結果リスト

4. **GET /api/v1/ai/image/history**
   - 認識履歴取得
   - クエリパラメータ: `limit`, `offset`
   - レスポンス: 認識履歴リスト

5. **POST /api/v1/ai/image/feedback**
   - 認識結果フィードバック送信
   - リクエスト: `{ image_hash, correct_ingredients, incorrect_ingredients, comment }`
   - レスポンス: 処理結果

6. **GET /api/v1/ai/image/ingredients/{ingredient_id}**
   - 食材詳細情報取得
   - レスポンス: 食材情報

7. **GET /api/v1/ai/image/ingredients**
   - 食材検索
   - クエリパラメータ: `query`, `category`
   - レスポンス: 検索結果リスト

8. **GET /api/v1/ai/image/categories**
   - カテゴリ一覧取得
   - レスポンス: カテゴリリスト

### 3. フロントエンドコンポーネント

#### `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/frontend/components/IngredientScanner.jsx`
- **機能**
  - カメラ起動・撮影
  - ファイルアップロード
  - 画像プレビュー
  - リアルタイム認識
  - 認識結果一覧表示
  - 食材選択（チェックボックス）
  - レシピ検索へ遷移

- **状態管理**
  - `cameraActive` - カメラ起動状態
  - `capturedImage` - 撮影画像
  - `recognitionResults` - 認識結果
  - `selectedIngredients` - 選択された食材
  - `loading` - ローディング状態
  - `error` - エラーメッセージ

- **主要機能**
  - `startCamera()` - カメラ起動（背面カメラ優先）
  - `capturePhoto()` - 写真撮影
  - `recognizeImage()` - 画像認識API呼び出し
  - `toggleIngredientSelection()` - 食材選択トグル
  - `searchRecipesByIngredients()` - レシピ検索へ遷移

#### `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/frontend/components/IngredientScanner.css`
- レスポンシブデザイン
- カメラプレビュースタイル
- 認識結果カードスタイル
- ローディングアニメーション
- モバイル対応

### 4. テストコード

#### `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/tests/test_image_recognition_service.py`
- **テストクラス**
  - `TestImageRecognitionService` - 基本機能テスト
  - `TestIntegrationScenarios` - 統合シナリオテスト

- **テストカバレッジ**
  - 初期化テスト
  - ファイル認識テスト
  - Base64認識テスト
  - URL認識テスト（モックモード）
  - 画像前処理テスト
  - 画像ハッシュテスト
  - キャッシュ機能テスト
  - 食材情報取得テスト
  - 食材検索テスト
  - カテゴリ取得テスト
  - モック結果品質テスト
  - 食材辞書構造テスト
  - 最大結果数制限テスト
  - 並行認識テスト
  - シングルトンインスタンステスト
  - 画像フォーマットサポートテスト
  - エラーハンドリングテスト
  - キャッシュ有効期限テスト
  - 部分一致検索テスト
  - カテゴリフィルタリングテスト
  - 日本語食材名テスト
  - 完全な認識ワークフローテスト
  - 複数画像認識テスト

## 依存関係

### Python
- **Pillow (PIL)** - 画像処理ライブラリ
  - 画像読み込み
  - リサイズ
  - フォーマット変換
  - Base64エンコード・デコード

### JavaScript
- **React** - UIコンポーネント
- **MediaDevices API** - カメラアクセス
- **FileReader API** - ファイル読み込み

## 動作モード

### モックモード（デフォルト）
- 外部APIを使用せずランダムな食材を返す
- デモ・開発用途
- 信頼度スコアは降順で生成
- キャッシュ機能は有効

### 本番モード（TODO）
- 外部AI API統合準備済み
- OpenAI Vision API
- Google Cloud Vision API
- 認識精度向上

## データフロー

```
1. ユーザーがカメラ撮影 or ファイルアップロード
   ↓
2. フロントエンド: Base64エンコード
   ↓
3. API: POST /api/v1/ai/image/recognize
   ↓
4. サービス: 画像前処理（リサイズ、RGB変換）
   ↓
5. サービス: キャッシュチェック
   ↓
6. サービス: 画像認識（モック or 外部API）
   ↓
7. サービス: キャッシュ保存
   ↓
8. API: 認識結果返却
   ↓
9. フロントエンド: 結果表示・食材選択
   ↓
10. レシピ検索へ遷移（選択食材付き）
```

## キャッシュ仕様

- **キャッシュキー**: 画像のSHA256ハッシュ
- **保存先**: `data/cache/image_recognition/`
- **ファイル形式**: JSON
- **有効期限**: 24時間
- **構造**:
  ```json
  {
    "timestamp": "2025-12-11T10:30:00",
    "results": [
      {
        "ingredient_id": "tomato",
        "name": "トマト",
        "confidence": 0.95,
        ...
      }
    ]
  }
  ```

## レスポンス形式

### 認識結果
```json
{
  "status": "ok",
  "data": [
    {
      "ingredient_id": "tomato",
      "name": "トマト",
      "name_en": "Tomato",
      "category": "野菜",
      "confidence": 0.95,
      "keywords": ["赤", "丸い"]
    }
  ],
  "meta": {
    "mode": "mock",
    "max_results": 5,
    "total_found": 5
  }
}
```

### エラーレスポンス
```json
{
  "status": "error",
  "error": "Failed to recognize image: Invalid format",
  "data": null
}
```

## セキュリティ考慮事項

1. **ファイルサイズ制限**
   - アップロード画像は最大10MB（推奨）
   - 前処理で最大1024pxにリサイズ

2. **ファイル形式検証**
   - JPEG, PNG, BMP のみ許可
   - PIL による検証

3. **保存先制限**
   - `data/uploads/images/` ディレクトリのみ
   - タイムスタンプ付きファイル名

4. **キャッシュ管理**
   - 定期的なキャッシュクリア推奨
   - 古いキャッシュは自動削除

## 今後の拡張予定

### 外部API統合
- OpenAI Vision API 統合
- Google Cloud Vision API 統合
- Clarifai Food Model 統合

### 機能追加
- 複数食材の同時認識（バウンディングボックス）
- 食材の量・状態の推定（「切り済み」「生」など）
- レシピ自動提案（認識食材から）
- 学習機能（フィードバック活用）

### パフォーマンス改善
- 画像圧縮の最適化
- キャッシュ戦略の改善
- 並列処理対応

## 使用例

### 1. カメラ撮影から認識
```jsx
// IngredientScannerコンポーネントを使用
<IngredientScanner />
```

### 2. API直接呼び出し
```python
from backend.services.image_recognition_service import get_image_recognition_service

service = get_image_recognition_service()
results = service.recognize_from_file(Path("test.jpg"), max_results=5)

for result in results:
    print(f"{result['name']}: {result['confidence']*100:.1f}%")
```

### 3. Base64画像認識
```javascript
const response = await fetch('/api/v1/ai/image/recognize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    image_base64: base64ImageData,
    max_results: 5
  })
});

const result = await response.json();
console.log(result.data);
```

## テスト実行

```bash
# 全テスト実行
pytest backend/tests/test_image_recognition_service.py -v

# カバレッジ付き
pytest backend/tests/test_image_recognition_service.py --cov=backend.services.image_recognition_service

# 特定テストのみ
pytest backend/tests/test_image_recognition_service.py::TestImageRecognitionService::test_recognize_from_file
```

## トラブルシューティング

### カメラが起動しない
- HTTPSまたはlocalhostで実行していることを確認
- ブラウザのカメラ許可設定を確認
- ファイルアップロードで代替可能

### 認識結果が返らない
- モックモードで動作しているか確認
- 画像形式が対応しているか確認（JPEG, PNG, BMP）
- ファイルサイズが適切か確認

### キャッシュが効かない
- `data/cache/image_recognition/` ディレクトリの書き込み権限を確認
- キャッシュディレクトリが存在するか確認

## 実装完了日
2025-12-11

## 関連Phase
- Phase 12-1: レシピAI分析基盤
- Phase 12-3: 栄養価自動計算（予定）
- Phase 12-4: 献立自動提案（予定）
