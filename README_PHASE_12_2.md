# Phase 12-2: 食材画像認識機能 - README

## 概要
Personal Recipe Intelligence の食材画像認識機能です。カメラ撮影またはファイルアップロードから食材を自動識別し、レシピ検索に活用できます。

## 機能
- カメラ撮影による食材認識
- ファイルアップロード対応
- 100種類以上の日本の一般的な食材に対応
- 信頼度スコア付き認識結果
- 複数食材の同時認識
- 認識結果キャッシュ（24時間）
- レシピ検索への連携

## 対応食材カテゴリ
- 野菜（30種類以上）
- 肉類（7種類）
- 魚介類（10種類）
- 卵・乳製品（5種類）
- 穀物・麺類（7種類）
- 豆類（4種類）
- 調味料（10種類）
- 果物（10種類）
- その他（20種類以上）

## セットアップ

### 依存関係インストール
```bash
# Python依存関係
pip install Pillow fastapi uvicorn pydantic pytest

# または requirements.txt から
pip install -r backend/requirements.txt
```

### ディレクトリ作成
```bash
mkdir -p data/uploads/images
mkdir -p data/cache/image_recognition
```

## 使用方法

### 1. サービス単体での使用

```python
from backend.services.image_recognition_service import get_image_recognition_service
from pathlib import Path

# サービス取得（モックモード）
service = get_image_recognition_service(mode="mock")

# ファイルから認識
results = service.recognize_from_file(Path("image.jpg"), max_results=5)

# 結果表示
for result in results:
    print(f"{result['name']}: {result['confidence']*100:.1f}%")
```

### 2. API経由での使用

#### API起動
```bash
cd backend
python -m api.main
```

#### Base64画像で認識
```bash
curl -X POST "http://localhost:8000/api/v1/ai/image/recognize" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "BASE64_ENCODED_IMAGE_DATA",
    "max_results": 5
  }'
```

#### ファイルアップロード
```bash
curl -X POST "http://localhost:8000/api/v1/ai/image/recognize-file" \
  -F "file=@image.jpg" \
  -F "max_results=5"
```

### 3. フロントエンドコンポーネント

```jsx
import IngredientScanner from './components/IngredientScanner';

function App() {
  return (
    <div>
      <h1>食材スキャナー</h1>
      <IngredientScanner />
    </div>
  );
}
```

## APIエンドポイント

### 画像認識
- `POST /api/v1/ai/image/recognize` - Base64画像から認識
- `POST /api/v1/ai/image/recognize-file` - ファイルアップロード
- `POST /api/v1/ai/image/recognize-url` - URL画像から認識

### 認識履歴
- `GET /api/v1/ai/image/history` - 認識履歴取得
- `POST /api/v1/ai/image/feedback` - フィードバック送信

### 食材情報
- `GET /api/v1/ai/image/ingredients/{id}` - 食材詳細取得
- `GET /api/v1/ai/image/ingredients?query=トマト` - 食材検索
- `GET /api/v1/ai/image/categories` - カテゴリ一覧

## テスト実行

```bash
# 全テスト実行
pytest backend/tests/test_image_recognition_service.py -v

# カバレッジ付き
pytest backend/tests/test_image_recognition_service.py --cov

# 使用例デモ
python examples/test_image_recognition.py
```

## レスポンス例

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
    },
    {
      "ingredient_id": "onion",
      "name": "玉ねぎ",
      "name_en": "Onion",
      "category": "野菜",
      "confidence": 0.85,
      "keywords": ["茶色", "球"]
    }
  ],
  "meta": {
    "mode": "mock",
    "max_results": 5,
    "total_found": 2
  }
}
```

## 動作モード

### モックモード（デフォルト）
開発・デモ用。ランダムな食材を返します。
```python
service = get_image_recognition_service(mode="mock")
```

### 本番モード（準備中）
外部AI API統合。OpenAI Vision、Google Cloud Vision等に対応予定。
```python
service = get_image_recognition_service(mode="production")
```

## パフォーマンス

- 画像前処理: 最大1024pxにリサイズ
- キャッシュ: 24時間有効
- 認識速度（モック）: ~10ms
- 認識速度（キャッシュヒット）: ~1ms

## セキュリティ

1. **ファイルサイズ制限**
   - 推奨最大: 10MB
   - 自動リサイズ: 1024px以下

2. **ファイル形式**
   - 対応: JPEG, PNG, BMP
   - PIL による検証

3. **保存先**
   - `data/uploads/images/` 配下のみ
   - タイムスタンプ付きファイル名

## トラブルシューティング

### カメラが起動しない
- HTTPSまたはlocalhostで実行してください
- ブラウザのカメラ許可を確認してください
- ファイルアップロードも利用可能です

### 画像認識が失敗する
- 対応形式（JPEG, PNG, BMP）を確認してください
- ファイルサイズが適切か確認してください
- モックモードで動作しているか確認してください

### キャッシュが効かない
- `data/cache/image_recognition/` の書き込み権限を確認してください
- ディレクトリが存在するか確認してください

## 今後の拡張

### 外部API統合
- OpenAI Vision API
- Google Cloud Vision API
- Clarifai Food Model

### 機能追加
- バウンディングボックス表示
- 食材の量・状態推定
- レシピ自動提案
- フィードバック学習

## ライセンス
MIT

## 関連ドキュメント
- [Phase 12-2 実装詳細](/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/docs/PHASE_12_2_IMAGE_RECOGNITION.md)
- [CLAUDE.md - 開発ルール](/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/CLAUDE.md)

## 実装ファイル一覧
```
backend/
  services/
    image_recognition_service.py    # 画像認識サービス
  api/
    routers/
      image_recognition.py           # APIルーター
  tests/
    test_image_recognition_service.py # テストコード

frontend/
  components/
    IngredientScanner.jsx            # スキャナーコンポーネント
    IngredientScanner.css            # スタイル

examples/
  test_image_recognition.py          # 使用例

docs/
  PHASE_12_2_IMAGE_RECOGNITION.md    # 実装ドキュメント
```

## サポート
- Issue: GitHubリポジトリ
- Email: プロジェクトメンテナー

---

**Personal Recipe Intelligence - Phase 12-2**
実装日: 2025-12-11
