# レビュー・評価機能 ガイド

Personal Recipe Intelligence のレビュー・評価機能の使用ガイドです。

## 機能概要

### 実装機能

1. **星評価（1-5）**
   - レシピに対して1〜5の星で評価
   - 平均評価の自動計算
   - 評価分布の可視化

2. **コメント投稿**
   - 最大2000文字のレビューコメント
   - XSS対策済み（自動HTMLエスケープ）
   - 改行対応

3. **役に立った機能**
   - レビューに「役に立った」をマーク
   - マーク数による人気レビュー表示
   - マーク/解除の切り替え

4. **レビュー管理**
   - 自分のレビューの編集・削除
   - 編集履歴の記録（updated_at）
   - 権限チェック

5. **ソート・フィルター**
   - 新着順
   - 評価順（星が高い順）
   - 役に立った順

## アーキテクチャ

```
┌─────────────────┐
│  RecipeReviews  │  ← メインコンポーネント
│     (React)     │
└────────┬────────┘
         │
         ├─ RatingSummary     ← 評価サマリー表示
         ├─ ReviewForm        ← レビュー投稿フォーム
         └─ ReviewList        ← レビュー一覧
             └─ ReviewItem    ← 個別レビュー

┌─────────────────┐
│  Review Router  │  ← FastAPI エンドポイント
│   (FastAPI)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Review Service  │  ← ビジネスロジック
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ reviews.json    │  ← データ永続化
└─────────────────┘
```

## セットアップ

### 1. バックエンド

```bash
# 依存関係のインストール（既存環境に追加）
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
pip install fastapi pydantic

# データディレクトリの作成
mkdir -p data/reviews

# テストの実行
pytest backend/tests/test_review_service.py -v
pytest backend/tests/test_review_api.py -v
```

### 2. フロントエンド

```bash
# コンポーネントの配置確認
ls -la frontend/components/RecipeReviews.jsx
ls -la frontend/components/RecipeReviews.css

# React アプリへの統合（例）
# App.jsx または RecipeDetail.jsx に以下を追加：
```

```jsx
import RecipeReviews from './components/RecipeReviews';

function RecipeDetail({ recipeId }) {
  return (
    <div>
      {/* レシピ詳細 */}
      <RecipeReviews recipeId={recipeId} />
    </div>
  );
}
```

### 3. APIルーターの登録

`backend/api/main.py` にルーターを追加：

```python
from fastapi import FastAPI
from backend.api.routers import review

app = FastAPI()
app.include_router(review.router)
```

## 使用方法

### フロントエンド（React）

```jsx
import RecipeReviews from './components/RecipeReviews';

// レシピ詳細ページで使用
<RecipeReviews recipeId="recipe123" />
```

コンポーネントは以下を自動的に処理します：
- レビュー一覧の表示
- 評価サマリーの表示
- レビュー投稿フォーム
- ソート切り替え
- 役に立ったボタン

### バックエンド（Python）

```python
from backend.services.review_service import ReviewService

# サービスの初期化
service = ReviewService()

# レビュー作成
review = service.create_review(
    recipe_id="recipe1",
    user_id="user1",
    rating=5,
    comment="とても美味しかったです！"
)

# レビュー一覧取得
reviews = service.get_recipe_reviews("recipe1", sort_by="rating")

# 評価サマリー取得
summary = service.get_recipe_rating_summary("recipe1")
print(f"Average: {summary.average_rating}")
print(f"Total: {summary.total_reviews}")

# 役に立ったマーク
service.mark_helpful(review.id, "user2")

# 人気レビュー取得
popular = service.get_popular_reviews("recipe1", limit=3)
```

## データモデル

### Review

```python
@dataclass
class Review:
    id: str                      # UUID
    recipe_id: str               # レシピID
    user_id: str                 # ユーザーID
    rating: int                  # 評価 (1-5)
    comment: str                 # コメント (最大2000文字)
    helpful_count: int           # 役に立った数
    helpful_users: list[str]     # マークしたユーザーIDリスト
    created_at: datetime         # 作成日時
    updated_at: Optional[datetime]  # 更新日時
```

### RecipeRatingSummary

```python
@dataclass
class RecipeRatingSummary:
    recipe_id: str                        # レシピID
    average_rating: float                 # 平均評価 (小数第1位)
    total_reviews: int                    # レビュー総数
    rating_distribution: dict[int, int]   # 評価分布 {1: 0, 2: 1, ...}
```

## セキュリティ

### 実装済み対策

1. **XSS対策**
   - コメントのHTMLエスケープ
   - `html.escape()` による自動サニタイズ

2. **認証・認可**
   - Bearer Token による認証
   - 編集・削除時の権限チェック
   - 本人のみレビュー編集可能

3. **入力検証**
   - Pydantic によるバリデーション
   - rating は 1-5 の範囲制限
   - comment は 2000文字制限

4. **重複防止**
   - 同一ユーザーの重複レビュー防止
   - 役に立ったの重複マーク防止

## パフォーマンス

### 最適化ポイント

1. **データ構造**
   - JSONファイルベース（個人用途に最適）
   - メモリキャッシュ不要

2. **ソート**
   - サービス層でのソート処理
   - 新着順、評価順、人気順対応

3. **計算**
   - 平均評価はリアルタイム計算
   - helpful_count はマーク時に更新

## テスト

### サービスのテスト

```bash
# 全テスト実行
pytest backend/tests/test_review_service.py -v

# 特定のテスト
pytest backend/tests/test_review_service.py::TestReviewService::test_create_review -v

# カバレッジ
pytest backend/tests/test_review_service.py --cov=backend.services.review_service --cov-report=html
```

### APIのテスト

```bash
# 全テスト実行
pytest backend/tests/test_review_api.py -v

# 特定のテスト
pytest backend/tests/test_review_api.py::TestReviewAPI::test_create_review -v
```

### カバレッジ目標

- サービス層: 90%以上
- API層: 80%以上
- 全体: 85%以上

## トラブルシューティング

### 問題: レビューが保存されない

```bash
# データディレクトリの確認
ls -la data/reviews/

# 権限の確認
chmod 755 data/reviews

# ログの確認
tail -f logs/app.log
```

### 問題: XSS攻撃の懸念

```python
# サニタイズ処理の確認
from backend.services.review_service import ReviewService

service = ReviewService()
review = service.create_review(
    recipe_id="test",
    user_id="test",
    rating=5,
    comment="<script>alert('test')</script>"
)

# エスケープされていることを確認
assert "<script>" not in review.comment
assert "&lt;script&gt;" in review.comment
```

### 問題: パフォーマンスの低下

```python
# レビュー数の確認
service = ReviewService()
reviews = service.get_recipe_reviews("recipe1")
print(f"Total reviews: {len(reviews)}")

# 大量のレビューがある場合はlimitを使用
limited_reviews = service.get_recipe_reviews("recipe1", limit=20)
```

## 今後の拡張

### 候補機能

1. **画像付きレビュー**
   - 料理写真のアップロード
   - サムネイル生成

2. **レビューへの返信**
   - スレッド形式のディスカッション
   - ネスト表示

3. **レポート機能**
   - 不適切なレビューの報告
   - モデレーション機能

4. **通知機能**
   - 新規レビューの通知
   - 役に立ったの通知

5. **統計機能**
   - ユーザー別統計
   - レシピ別トレンド分析

## ライセンス

MIT License - 個人プロジェクトのため自由に改変可能

## 関連ドキュメント

- [API仕様書](./REVIEW_API.md)
- [CLAUDE.md](../CLAUDE.md)
- [メインREADME](../README.md)
