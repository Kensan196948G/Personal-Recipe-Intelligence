# 海外レシピ画像取得機能 - 実装完了サマリー

## 概要
海外レシピAPI（Spoonacular等）や外部サイトから取得したレシピ画像を自動的にダウンロードし、ローカルに保存する機能を実装しました。

## 実装内容

### 1. データベーススキーマ拡張

#### Recipeモデルへのフィールド追加
- **image_url**: 元画像のURL（Optional[str]）
- **image_path**: ローカル保存パス（Optional[str]）

#### Alembicマイグレーション
- マイグレーションファイル: `alembic/versions/add_image_fields_to_recipe.py`
- テーブル: `recipe`
- カラム追加: `image_url`, `image_path`
- 実行済み: `alembic upgrade head`

### 2. ImageDownloadService実装

**ファイル**: `backend/services/image_download_service.py`

#### 主要機能
- **download_and_save()**: 画像URLからダウンロード・保存
  - URLバリデーション（http/https のみ許可）
  - ファイルサイズチェック（最大10MB）
  - 拡張子チェック（.jpg, .jpeg, .png, .gif, .webp）
  - Content-Type検証
  - ディレクトリトラバーサル対策
  - タイムアウト設定（30秒）

- **get_image_path()**: レシピIDから画像パスを検索
- **delete_image()**: 画像ファイルを削除

#### セキュリティ対策
- ディレクトリトラバーサル攻撃対策（絶対パス検証）
- ファイルサイズ制限
- 許可された拡張子のみ受け入れ
- タイムアウト設定

#### ファイル命名規則
- `{recipe_id}_{url_hash}.{ext}`
- url_hashはMD5ハッシュの先頭8文字
- 同じURLなら同じファイル名になる（重複防止）

### 3. RecipeCollector統合

**ファイル**: `backend/services/recipe_collector.py`

#### 変更内容
- ImageDownloadServiceをインスタンス化
- `save_recipe()`メソッドを非同期化（async/await対応）
- `translate_recipe()`でimage_urlを含めるように修正
- 画像ダウンロード失敗時もレシピ保存は継続（エラーハンドリング）
- `collect_random_recipes()`と`collect_recipes_by_search()`を非同期化

### 4. ExternalRecipeService統合

**ファイル**: `backend/services/external_recipe_service.py`

#### 変更内容
- ImageDownloadServiceをインスタンス化
- `import_recipe()`メソッドに`recipe_id`パラメータを追加
- recipe_idが指定されている場合のみ画像をダウンロード
- 画像取得失敗時もレシピインポートは継続

### 5. API更新

#### スキーマ更新（backend/api/schemas.py）
- **RecipeCreate**: `image_url`フィールド追加
- **RecipeRead**: `image_url`, `image_path`フィールド追加
- **RecipeUpdate**: `image_url`フィールド追加
- **RecipeListItem**: `image_url`, `image_path`フィールド追加

#### エンドポイント更新（backend/api/routers/recipes.py）

**新規エンドポイント**:
- `GET /api/v1/recipes/images/{filename}`: 画像ファイル配信
  - セキュリティ: ディレクトリトラバーサル対策
  - Content-Typeを拡張子から判定
  - FileResponseで配信

**既存エンドポイント更新**:
- `GET /api/v1/recipes`: image_url, image_pathを返却
- `GET /api/v1/recipes/{id}`: image_url, image_pathを返却
- `POST /api/v1/recipes`: image_urlを受け付け
- `PUT /api/v1/recipes/{id}`: image_urlを受け付け

### 6. RecipeService更新

**ファイル**: `backend/services/recipe_service.py`

- `create_recipe()`: `image_url`パラメータ追加
- `update_recipe()`: `image_url`パラメータ追加

## 使用方法

### 1. Spoonacularからのレシピ取得（自動画像ダウンロード）

```python
from backend.services.recipe_collector import RecipeCollector
from backend.core.database import get_session

collector = RecipeCollector(
    spoonacular_key="YOUR_API_KEY",
    deepl_key="YOUR_DEEPL_KEY"
)

with get_session() as session:
    # ランダムなレシピを5件取得（画像も自動ダウンロード）
    recipes = await collector.collect_random_recipes(session, count=5)
```

### 2. 外部サイトからのレシピインポート（手動画像ダウンロード）

```python
from backend.services.external_recipe_service import ExternalRecipeService

service = ExternalRecipeService()

# レシピをインポート（recipe_idを指定すると画像もダウンロード）
recipe_data = await service.import_recipe(
    url="https://example.com/recipe",
    html=html_content,
    recipe_id=123  # 既にDBに保存済みのレシピID
)
```

### 3. API経由でのレシピ作成

```bash
# レシピ作成（image_urlを指定）
curl -X POST "http://localhost:8001/api/v1/recipes" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Recipe",
    "image_url": "https://example.com/image.jpg",
    "ingredients": [],
    "steps": []
  }'

# レシピ取得（image_url, image_pathが含まれる）
curl "http://localhost:8001/api/v1/recipes/123"

# 画像ファイル取得
curl "http://localhost:8001/api/v1/recipes/images/123_abc12345.jpg" > recipe.jpg
```

## エラーハンドリング

- 画像ダウンロード失敗時もレシピ保存は継続
- エラーはログに記録（logger.error / logger.warning）
- HTTPエラー、タイムアウト、ファイルサイズ超過などを処理
- 無効なURL、対応していない形式は自動的にスキップ

## テスト

**ファイル**: `backend/tests/test_image_download_service.py`

- URLバリデーションテスト
- 拡張子判定テスト
- ファイル名生成テスト
- ダウンロード成功・失敗テスト
- ファイルサイズチェックテスト
- ディレクトリトラバーサル対策テスト

## ディレクトリ構造

```
data/
└── images/              # 画像保存ディレクトリ
    ├── 1_a1b2c3d4.jpg  # レシピID 1の画像
    ├── 2_e5f6g7h8.png  # レシピID 2の画像
    └── ...
```

## セキュリティ考慮事項

1. **ディレクトリトラバーサル対策**
   - 絶対パスの検証
   - ファイル名の検証（..、/、\ を禁止）

2. **ファイルサイズ制限**
   - 最大10MB
   - Content-Lengthヘッダーと実際のサイズを両方チェック

3. **許可された形式のみ**
   - .jpg, .jpeg, .png, .gif, .webp のみ許可

4. **タイムアウト設定**
   - ダウンロードは30秒でタイムアウト

5. **URL検証**
   - http/https のみ許可
   - URLスキームとネットロケーションを検証

## 今後の拡張案

1. 画像リサイズ・最適化機能
2. サムネイル生成
3. CDN連携
4. 画像のメタデータ抽出
5. 重複画像の検出・削除

## 関連ドキュメント

- [API仕様書](../03_API仕様書(api-specification)/レシピAPI(recipe-api).md)
- [データベース設計](../04_データベース(database)/テーブル定義書(table-definitions).md)
- [セキュリティガイドライン](../08_セキュリティ(security)/セキュリティガイドライン(security-guidelines).md)
