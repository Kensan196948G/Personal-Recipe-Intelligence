# レシピ推薦AI機能ドキュメント

## 概要

Personal Recipe Intelligence (PRI) のレシピ推薦AI機能は、ユーザーの行動履歴と嗜好を分析し、パーソナライズされたレシピ推薦を提供します。

## 主要機能

### 1. ハイブリッド推薦アルゴリズム

複数の推薦手法を組み合わせた高精度な推薦システム:

- **協調フィルタリング (30%)**: 類似ユーザーの好みを参考
- **コンテンツベースフィルタリング (50%)**: レシピの特徴（食材、カテゴリ、タグ）の類似性
- **トレンドスコア (10%)**: 最近人気のレシピ
- **多様性ペナルティ (10%)**: 似たレシピばかり推薦しない

### 2. ユーザー行動分析

以下の行動データを記録・分析:

- **viewed**: レシピ閲覧
- **cooked**: レシピで調理
- **rated**: レシピ評価
- **favorited**: お気に入り登録
- **dismissed**: 興味なし

### 3. 嗜好分析

ユーザーの好みを多角的に分析:

- 好きな食材トップ10
- 好きなカテゴリ
- 好きなタグ
- 調理頻度（月間）
- 平均調理時間
- 好みの難易度

## API エンドポイント

### パーソナライズ推薦取得

```
GET /api/v1/ai/recommend
```

**クエリパラメータ:**
- `user_id` (必須): ユーザーID
- `limit` (任意): 取得件数（1-50、デフォルト: 10）

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "user_id": "user_001",
    "recommendations": [
      {
        "recipe": {
          "id": "recipe_001",
          "title": "カレーライス",
          "category": "主菜",
          "tags": ["簡単", "人気"],
          "cooking_time": 30,
          "difficulty": "easy",
          "ingredients": [...]
        },
        "score": 0.85,
        "reason": "あなたの好みに合っています、似た嗜好のユーザーに人気です",
        "match_percentage": 85
      }
    ],
    "total": 10
  }
}
```

### 類似レシピ取得

```
GET /api/v1/ai/recommend/similar/{recipe_id}
```

**パスパラメータ:**
- `recipe_id`: レシピID

**クエリパラメータ:**
- `limit` (任意): 取得件数（1-20、デフォルト: 5）

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "recipe_id": "recipe_001",
    "similar_recipes": [
      {
        "recipe": {...},
        "similarity": 0.75,
        "match_percentage": 75
      }
    ],
    "total": 5
  }
}
```

### トレンドレシピ取得

```
GET /api/v1/ai/recommend/trending
```

**クエリパラメータ:**
- `limit` (任意): 取得件数（1-50、デフォルト: 10）

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "trending_recipes": [
      {
        "recipe": {...},
        "score": 0.8,
        "reason": "最近人気のレシピです",
        "match_percentage": 80
      }
    ],
    "total": 10
  }
}
```

### 推薦フィードバック送信

```
POST /api/v1/ai/feedback
```

**リクエストボディ:**
```json
{
  "user_id": "user_001",
  "recipe_id": "recipe_001",
  "feedback_type": "interested",
  "metadata": {
    "context": "recommendation"
  }
}
```

**フィードバックタイプ:**
- `interested`: 興味あり
- `not_interested`: 興味なし
- `favorited`: お気に入り
- `cooked`: 調理した

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "message": "フィードバックを記録しました",
    "user_id": "user_001",
    "recipe_id": "recipe_001",
    "feedback_type": "interested"
  }
}
```

### ユーザー行動記録

```
POST /api/v1/ai/activity
```

**リクエストボディ:**
```json
{
  "user_id": "user_001",
  "recipe_id": "recipe_001",
  "activity_type": "viewed",
  "metadata": {
    "source": "search",
    "rating": 5
  }
}
```

**行動タイプ:**
- `viewed`: 閲覧
- `cooked`: 調理
- `rated`: 評価
- `favorited`: お気に入り
- `dismissed`: 却下

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "message": "行動を記録しました",
    "user_id": "user_001",
    "recipe_id": "recipe_001",
    "activity_type": "viewed"
  }
}
```

### ユーザー嗜好分析取得

```
GET /api/v1/ai/preferences
```

**クエリパラメータ:**
- `user_id` (必須): ユーザーID

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "user_id": "user_001",
    "total_activities": 50,
    "favorite_ingredients": [
      {"name": "じゃがいも", "count": 10},
      {"name": "玉ねぎ", "count": 8}
    ],
    "favorite_categories": [
      {"name": "主菜", "count": 15},
      {"name": "副菜", "count": 8}
    ],
    "favorite_tags": [
      {"name": "簡単", "count": 20},
      {"name": "時短", "count": 12}
    ],
    "cooking_frequency": 15,
    "average_cooking_time": 30,
    "preferred_difficulty": "easy"
  }
}
```

## アルゴリズム詳細

### 協調フィルタリング

1. **類似ユーザー検出**: Jaccard係数を使用してユーザー間の類似度を計算
2. **評価予測**: 類似ユーザーの行動に基づいてレシピへの関心度を予測
3. **重み付け**: ユーザー類似度に応じて評価を重み付け

```python
# ユーザー類似度（Jaccard係数）
similarity = |A ∩ B| / |A ∪ B|

# 評価予測
predicted_rating = Σ(similarity_i × rating_i) / Σ(similarity_i)
```

### コンテンツベースフィルタリング

1. **特徴抽出**: レシピから以下の特徴を抽出
   - 食材（weight: 1.0）
   - カテゴリ（weight: 2.0）
   - タグ（weight: 1.5）
   - 調理時間範囲（weight: 1.0）
   - 難易度（weight: 1.0）

2. **類似度計算**: コサイン類似度を使用

```python
# コサイン類似度
similarity = (A · B) / (||A|| × ||B||)

# 特徴ベクトルの例
features = {
  "ingredient:じゃがいも": 1.0,
  "category:主菜": 2.0,
  "tag:簡単": 1.5,
  "time:medium": 1.0,
  "difficulty:easy": 1.0
}
```

### トレンドスコア

直近30日のアクティビティ数をユーザー数で正規化:

```python
trend_score = min(recent_activities / total_users, 1.0)
```

### 多様性ペナルティ

直近7日の閲覧履歴で同じカテゴリの割合を計算:

```python
diversity_penalty = same_category_count / total_recent_activities
```

### 総合スコア

```python
total_score = (
  collaborative_score × 0.3 +
  content_score × 0.5 +
  trend_score × 0.1 -
  diversity_penalty × 0.1
)
```

## データ構造

### ユーザー行動データ (`data/user_activity.json`)

```json
{
  "user_001": [
    {
      "recipe_id": "recipe_001",
      "activity_type": "viewed",
      "timestamp": "2025-12-11T10:30:00.000Z",
      "metadata": {
        "source": "search"
      }
    }
  ]
}
```

### フィードバックデータ (`data/recommendation_feedback.json`)

```json
{
  "user_001": [
    {
      "recipe_id": "recipe_001",
      "feedback_type": "interested",
      "timestamp": "2025-12-11T10:35:00.000Z",
      "metadata": {
        "context": "recommendation"
      }
    }
  ]
}
```

### ユーザー嗜好データ (`data/user_preferences.json`)

自動計算されるため、手動編集不要。

## フロントエンド使用例

### RecommendationCard コンポーネント

```jsx
import RecommendationCard from '../components/RecommendationCard';

<RecommendationCard
  recommendation={{
    recipe: {...},
    score: 0.85,
    reason: "あなたの好みに合っています",
    match_percentage: 85
  }}
  onInterested={(recipeId) => console.log('興味あり:', recipeId)}
  onNotInterested={(recipeId) => console.log('興味なし:', recipeId)}
  onViewRecipe={(recipeId) => console.log('詳細表示:', recipeId)}
/>
```

### RecommendationsPage 使用例

```jsx
import RecommendationsPage from '../pages/RecommendationsPage';

<RecommendationsPage />
```

## 推薦品質向上のヒント

### 1. 初期データ収集

新規ユーザーには以下を提供:
- オンボーディングで好みの食材・カテゴリを選択
- トレンドレシピの表示
- 人気レシピの表示

### 2. フィードバックの活用

ユーザーに積極的にフィードバックを促す:
- 「興味あり」「興味なし」ボタン
- レシピ評価（5段階）
- 調理記録ボタン

### 3. データの鮮度管理

- 古い行動データ（90日以上）の重み減少
- 季節性を考慮（夏は冷製レシピ、冬は温かいレシピ）

### 4. A/Bテスト

推薦アルゴリズムの重み調整:
```python
# デフォルト
collaborative_weight = 0.3
content_weight = 0.5
trend_weight = 0.1
diversity_weight = 0.1

# テストパターン
# パターンA: コンテンツ重視
# パターンB: 協調重視
# パターンC: トレンド重視
```

## パフォーマンス最適化

### キャッシュ戦略

- ユーザー嗜好: 1時間キャッシュ
- トレンドレシピ: 30分キャッシュ
- 類似レシピ: 24時間キャッシュ

### バッチ処理

- 毎日深夜にユーザー嗜好を再計算
- トレンドスコアを事前計算

## テスト

### ユニットテスト実行

```bash
pytest backend/tests/test_recommendation_ai_service.py -v
pytest backend/tests/test_recommendation_ai_router.py -v
```

### テストカバレッジ

```bash
pytest backend/tests/test_recommendation_ai*.py --cov=backend/services/recommendation_ai_service --cov-report=html
```

## トラブルシューティング

### 推薦が表示されない

1. ユーザー行動データが記録されているか確認
2. レシピデータが正しく取得できているか確認
3. ログファイルでエラーを確認

### 推薦の質が低い

1. ユーザー行動データが十分か確認（最低10件推奨）
2. レシピデータの多様性を確認
3. アルゴリズムの重み調整

### パフォーマンスが遅い

1. レシピ数が多すぎる場合は事前フィルタリング
2. キャッシュの活用
3. 非同期処理の導入

## 今後の拡張

- [ ] 機械学習モデルの導入（scikit-learn、TensorFlow）
- [ ] リアルタイム推薦（WebSocket）
- [ ] グループ推薦（家族向け）
- [ ] 季節性・イベント対応
- [ ] 栄養バランス推薦
- [ ] 冷蔵庫の食材から推薦
- [ ] 調理スキルレベル対応
- [ ] ソーシャル機能（友人の推薦）

## ライセンス

MIT License
