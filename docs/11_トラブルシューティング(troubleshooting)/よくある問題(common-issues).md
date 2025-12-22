# よくある問題 (Common Issues)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) でよく発生する問題とその解決方法を記載する。

## 2. バックエンド関連

### 2.1 サーバーが起動しない

**症状**
```
ModuleNotFoundError: No module named 'xxx'
```

**原因**
- 依存関係が未インストール
- 仮想環境が有効化されていない

**解決策**
```bash
# 仮想環境を有効化
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt
```

---

### 2.2 データベース接続エラー

**症状**
```
sqlalchemy.exc.OperationalError: unable to open database file
```

**原因**
- データベースファイルが存在しない
- ディレクトリのパーミッション不足

**解決策**
```bash
# dataディレクトリ作成
mkdir -p data

# パーミッション確認
ls -la data/

# マイグレーション実行
alembic upgrade head
```

---

### 2.3 API 500エラー

**症状**
```json
{"status": "error", "error": {"code": "INTERNAL_ERROR"}}
```

**原因**
- 未処理の例外
- データベース不整合

**解決策**
```bash
# ログ確認
tail -100 logs/error.log

# デバッグモードで起動
uvicorn backend.api.main:app --reload --log-level debug
```

---

### 2.4 スクレイピング失敗

**症状**
```json
{"error": {"code": "SCRAPE_FAILED"}}
```

**原因**
- サイト構造の変更
- robots.txtでブロック
- タイムアウト

**解決策**
1. 対象URLを直接確認
2. robots.txtを確認
3. タイムアウト値を調整

```python
# タイムアウト延長
SCRAPING_CONFIG = {
    "timeout": 60  # 30 -> 60
}
```

---

### 2.5 翻訳エラー

**症状**
```json
{"error": {"code": "TRANSLATION_FAILED"}}
```

**原因**
- APIキーが未設定/無効
- クォータ超過
- ネットワークエラー

**解決策**
```bash
# APIキー確認
grep DEEPL .env

# クォータ確認
# DeepLダッシュボードで確認

# ネットワーク確認
curl -v https://api-free.deepl.com/v2/usage
```

## 3. フロントエンド関連

### 3.1 開発サーバーが起動しない

**症状**
```
error: Cannot find package 'xxx'
```

**原因**
- node_modulesが未インストール

**解決策**
```bash
cd frontend
rm -rf node_modules
bun install
```

---

### 3.2 API接続エラー

**症状**
```
Failed to fetch
CORS error
```

**原因**
- バックエンドが起動していない
- CORS設定の問題

**解決策**
1. バックエンドの起動確認
   ```bash
   curl http://localhost:8001/health
   ```

2. CORS設定確認
   ```python
   # backend/api/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       ...
   )
   ```

---

### 3.3 コンポーネントエラー

**症状**
```
Uncaught TypeError: Cannot read property 'xxx' of undefined
```

**原因**
- propsが未定義
- データの読み込み完了前にアクセス

**解決策**
```svelte
<!-- 条件付きレンダリング -->
{#if recipe}
  <RecipeDetail {recipe} />
{:else}
  <Loading />
{/if}
```

## 4. データベース関連

### 4.1 マイグレーションエラー

**症状**
```
alembic.util.exc.CommandError: Target database is not up to date.
```

**原因**
- マイグレーションの不整合

**解決策**
```bash
# 現在のバージョン確認
alembic current

# 手動でバージョン設定
alembic stamp head

# 再実行
alembic upgrade head
```

---

### 4.2 データベース破損

**症状**
```
sqlite3.DatabaseError: database disk image is malformed
```

**原因**
- 不正なシャットダウン
- ディスク障害

**解決策**
```bash
# 整合性チェック
sqlite3 data/pri.db "PRAGMA integrity_check;"

# バックアップから復元
cp data/backups/daily/latest/pri.db data/pri.db
```

## 5. OCR関連

### 5.1 テキスト抽出失敗

**症状**
```json
{"error": {"code": "NO_TEXT_DETECTED"}}
```

**原因**
- 画像品質が低い
- テキストがない画像

**解決策**
- より高解像度の画像を使用
- 照明を改善
- コントラストを上げる

---

### 5.2 構造化失敗

**症状**
- テキストは抽出されるが、材料・手順が正しく分離されない

**原因**
- 非標準的なレシピ形式
- 認識エラー

**解決策**
- プレビュー機能で確認後、手動で修正
- raw_text を確認し、パターンを調整

## 6. パフォーマンス関連

### 6.1 APIレスポンスが遅い

**症状**
- レスポンスに数秒かかる

**原因**
- N+1クエリ問題
- インデックス不足

**解決策**
```python
# 関連データを一括取得
statement = select(Recipe).options(
    selectinload(Recipe.ingredients),
    selectinload(Recipe.steps)
)

# インデックス追加
CREATE INDEX idx_recipe_title ON recipe(title);
```

---

### 6.2 メモリ使用量増加

**症状**
- 長時間稼働でメモリ使用量が増加

**原因**
- メモリリーク
- キャッシュ肥大化

**解決策**
```bash
# プロセス再起動
./scripts/restart.sh

# 定期再起動設定
# crontab で毎日再起動
0 4 * * * /path/to/project/scripts/restart.sh
```

## 7. 問題報告テンプレート

```markdown
## 問題の概要
[問題の簡潔な説明]

## 再現手順
1. [ステップ1]
2. [ステップ2]
3. [ステップ3]

## 期待される動作
[正常な場合の動作]

## 実際の動作
[発生した問題]

## 環境情報
- OS:
- Python:
- Node.js/Bun:

## ログ
[関連するログ出力]
```

## 8. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |
