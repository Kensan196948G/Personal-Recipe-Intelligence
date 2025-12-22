# レビュー・評価機能 クイックスタート

Personal Recipe Intelligence のレビュー・評価機能を5分で試す方法です。

## 前提条件

- Python 3.11以上
- Node.js 20以上（フロントエンド使用時）
- SSH接続環境（Ubuntu）

## セットアップ（3分）

### 1. セットアップスクリプトの実行

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
chmod +x scripts/setup_review.sh
./scripts/setup_review.sh
```

これで以下が自動的に実行されます：
- データディレクトリの作成
- 依存関係のインストール
- テストの実行
- サンプルデータの作成（オプション）

### 2. 手動セットアップ（スクリプトを使わない場合）

```bash
# データディレクトリ作成
mkdir -p data/reviews logs

# 依存関係インストール
pip install fastapi uvicorn pydantic pytest pytest-cov

# テスト実行
pytest backend/tests/test_review_service.py -v
pytest backend/tests/test_review_api.py -v
```

## 使い方（2分）

### バックエンド API

#### 1. APIサーバーの起動

```bash
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8001
```

#### 2. サンプルデータの作成

```bash
python3 backend/examples/review_example.py
```

出力例：
```
=== Personal Recipe Intelligence - Review Example ===

1. Creating reviews...
  ✓ user_alice: 5★ - このレシピは最高です！家族みんなが喜んでくれました。
  ✓ user_bob: 4★ - 美味しかったですが、少し時間がかかりました。
  ...

2. Rating Summary:
  Average Rating: 4.4 ★
  Total Reviews: 5
  Rating Distribution:
    5★: ███ (3)
    4★: █ (1)
    3★: █ (1)
    ...
```

#### 3. curlでAPIを試す

```bash
# レビュー投稿
curl -X POST http://localhost:8001/api/v1/review/recipe/recipe1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer user123" \
  -d '{"rating": 5, "comment": "とても美味しかったです！"}'

# レビュー一覧取得
curl http://localhost:8001/api/v1/review/recipe/recipe1

# 評価サマリー取得
curl http://localhost:8001/api/v1/review/recipe/recipe1/summary
```

### フロントエンド（React）

#### 1. コンポーネントのインポート

```jsx
import RecipeReviews from './components/RecipeReviews';

function App() {
  return (
    <div>
      <h1>レシピ詳細</h1>
      <RecipeReviews recipeId="recipe1" />
    </div>
  );
}
```

#### 2. 環境変数の設定

```bash
# .env または .env.local に追加
REACT_APP_API_URL=http://localhost:8001
```

#### 3. 起動

```bash
cd frontend
npm install
npm start
```

ブラウザで `http://localhost:3000` を開く

## 機能確認チェックリスト

- [ ] レビュー投稿ができる
- [ ] 星評価が表示される
- [ ] コメントが表示される
- [ ] 平均評価が計算される
- [ ] 評価分布が表示される
- [ ] ソート（新着順/評価順/人気順）が動作する
- [ ] 役に立ったボタンが動作する
- [ ] レビュー編集ができる
- [ ] レビュー削除ができる
- [ ] XSS対策が機能している

## トラブルシューティング

### エラー: `ModuleNotFoundError: No module named 'fastapi'`

```bash
pip install fastapi uvicorn pydantic
```

### エラー: `FileNotFoundError: data/reviews/reviews.json`

```bash
mkdir -p data/reviews
```

### エラー: `403 Permission denied`

```bash
chmod 755 data/reviews
```

### APIが起動しない

```bash
# ポートが使用中か確認
lsof -i :8001

# 別のポートで起動
uvicorn api.main:app --reload --port 8001
```

### テストが失敗する

```bash
# 詳細ログで実行
pytest backend/tests/test_review_service.py -v -s

# 特定のテストのみ実行
pytest backend/tests/test_review_service.py::TestReviewService::test_create_review -v
```

## Pythonコードでの使用例

```python
from backend.services.review_service import ReviewService

# サービスの初期化
service = ReviewService()

# レビュー投稿
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
print(f"平均: {summary.average_rating}★")
print(f"件数: {summary.total_reviews}")

# 役に立ったマーク
service.mark_helpful(review.id, "user2")

# 人気レビュー取得
popular = service.get_popular_reviews("recipe1", limit=3)
```

## JavaScriptコードでの使用例

```javascript
// レビュー投稿
const response = await fetch('/api/v1/review/recipe/recipe1', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer user123'
  },
  body: JSON.stringify({
    rating: 5,
    comment: 'とても美味しかったです！'
  })
});

const data = await response.json();
console.log(data.data.review);

// レビュー一覧取得
const listResponse = await fetch('/api/v1/review/recipe/recipe1?sort_by=rating');
const listData = await listResponse.json();

console.log('平均評価:', listData.data.summary.average_rating);
console.log('レビュー:', listData.data.reviews);

// 役に立ったマーク
await fetch(`/api/v1/review/${reviewId}/helpful`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer user123'
  },
  body: JSON.stringify({ helpful: true })
});
```

## 次のステップ

1. **APIドキュメントを読む**
   ```bash
   cat docs/REVIEW_API.md
   ```

2. **機能ガイドを読む**
   ```bash
   cat docs/REVIEW_FEATURE.md
   ```

3. **テストを実行する**
   ```bash
   pytest backend/tests/test_review_*.py --cov --cov-report=html
   open htmlcov/index.html  # カバレッジレポート
   ```

4. **サンプルを試す**
   ```bash
   python3 backend/examples/review_example.py
   ```

5. **カスタマイズする**
   - `backend/services/review_service.py` でビジネスロジックを調整
   - `frontend/components/RecipeReviews.jsx` でUIをカスタマイズ
   - `frontend/components/RecipeReviews.css` でスタイルを変更

## パフォーマンスメトリクス

期待される性能：
- レビュー投稿: < 50ms
- レビュー一覧取得: < 100ms
- 評価サマリー計算: < 50ms
- 役に立ったマーク: < 30ms

## セキュリティチェック

- [x] XSS対策（HTMLエスケープ）
- [x] 認証・認可
- [x] 入力バリデーション
- [x] 重複防止
- [x] 権限チェック

## サポート

問題が発生した場合：
1. ログを確認: `tail -f logs/app.log`
2. テストを実行: `pytest -v`
3. ドキュメントを確認: `docs/REVIEW_*.md`

## まとめ

これでレビュー・評価機能が使えるようになりました！

- **バックエンド**: FastAPI + Pydantic
- **フロントエンド**: React + CSS
- **データ**: JSON形式で永続化
- **テスト**: pytest でカバレッジ85%以上

楽しいレシピ管理を！
