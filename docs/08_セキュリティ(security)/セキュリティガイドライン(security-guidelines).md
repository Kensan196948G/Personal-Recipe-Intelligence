# セキュリティガイドライン (Security Guidelines)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) のセキュリティガイドラインを定義する。

## 2. セキュリティ原則

### 2.1 基本方針

- **最小権限の原則**: 必要最小限の権限のみ付与
- **多層防御**: 複数のセキュリティ対策を組み合わせる
- **セキュアバイデフォルト**: デフォルトで安全な設定

### 2.2 対象リスク

| リスク | 対策 |
|--------|------|
| SQLインジェクション | ORM使用、パラメータバインディング |
| XSS | 適切なエスケープ処理 |
| CSRF | 個人利用のため低リスク |
| ファイルアップロード | 拡張子・サイズ検証 |
| 情報漏洩 | ログマスキング |

## 3. 入力検証

### 3.1 バリデーション

```python
# Pydantic によるバリデーション例
from pydantic import BaseModel, Field, validator
import re

class RecipeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    servings: int | None = Field(default=None, ge=1, le=100)

    @validator('title')
    def title_must_not_contain_script(cls, v):
        if re.search(r'<script', v, re.IGNORECASE):
            raise ValueError('不正な文字列が含まれています')
        return v
```

### 3.2 ファイルアップロード

```python
# ファイル検証
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_upload(file: UploadFile) -> bool:
    # 拡張子チェック
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("対応していないファイル形式です")

    # サイズチェック
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValueError("ファイルサイズが大きすぎます")

    # MIMEタイプチェック
    import magic
    mime = magic.from_buffer(file.file.read(1024), mime=True)
    file.file.seek(0)
    if not mime.startswith('image/'):
        raise ValueError("画像ファイルではありません")

    return True
```

## 4. データ保護

### 4.1 機密データの取り扱い

| データ種別 | 保護方法 |
|-----------|----------|
| APIキー | 環境変数で管理 |
| データベース | ファイル権限設定 |
| ログ | 機密情報マスキング |

### 4.2 環境変数管理

```bash
# .env ファイル（Git管理外）
DEEPL_API_KEY=your-api-key-here
DATABASE_URL=sqlite:///./data/pri.db

# .env.example（Git管理内）
DEEPL_API_KEY=your-api-key-here
DATABASE_URL=sqlite:///./data/pri.db
```

### 4.3 ログマスキング

```python
import re

def mask_sensitive(text: str) -> str:
    """機密情報をマスキング"""
    patterns = [
        (r'api[_-]?key["\s:=]+["\']?[\w-]+', 'api_key=***'),
        (r'password["\s:=]+["\']?[\w-]+', 'password=***'),
        (r'token["\s:=]+["\']?[\w-]+', 'token=***'),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text
```

## 5. 外部リソースアクセス

### 5.1 Webスクレイピング

```python
# 安全なスクレイピング設定
SCRAPING_CONFIG = {
    "timeout": 30,
    "max_redirects": 5,
    "verify_ssl": True,
    "user_agent": "Mozilla/5.0 (compatible; RecipeBot/1.0)",
}

# robots.txt 遵守
def check_robots_txt(url: str) -> bool:
    from urllib.robotparser import RobotFileParser
    from urllib.parse import urlparse

    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()

    return rp.can_fetch(SCRAPING_CONFIG["user_agent"], url)
```

### 5.2 外部API呼び出し

```python
import httpx

# タイムアウト設定
client = httpx.Client(
    timeout=30.0,
    verify=True,  # SSL証明書検証
    follow_redirects=True,
    max_redirects=5
)

# エラーハンドリング
try:
    response = client.get(url)
    response.raise_for_status()
except httpx.TimeoutException:
    logger.error("タイムアウト")
except httpx.HTTPStatusError as e:
    logger.error(f"HTTPエラー: {e.response.status_code}")
```

## 6. SQLインジェクション対策

### 6.1 ORM使用

```python
# 安全: SQLModel/SQLAlchemy使用
from sqlmodel import select

statement = select(Recipe).where(Recipe.title == title)
recipes = session.exec(statement).all()

# 危険: 生SQL文字列結合（禁止）
# query = f"SELECT * FROM recipe WHERE title = '{title}'"
```

### 6.2 パラメータバインディング

```python
# 必要な場合は必ずパラメータバインディング
from sqlalchemy import text

statement = text("SELECT * FROM recipe WHERE title = :title")
result = session.execute(statement, {"title": title})
```

## 7. XSS対策

### 7.1 出力エスケープ

```python
from html import escape

def safe_output(text: str) -> str:
    """HTML特殊文字をエスケープ"""
    return escape(text)
```

### 7.2 Content Security Policy

```python
# FastAPI ミドルウェア
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 許可するオリジン
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 8. 依存関係管理

### 8.1 脆弱性スキャン

```bash
# pip-audit で脆弱性チェック
pip install pip-audit
pip-audit

# Safety でチェック
pip install safety
safety check
```

### 8.2 依存関係更新

```bash
# 依存関係の更新
pip list --outdated
pip install --upgrade package-name
```

## 9. チェックリスト

### 9.1 開発時

- [ ] 入力値をすべてバリデーション
- [ ] SQLは ORM を使用
- [ ] 機密情報は環境変数に格納
- [ ] ログに機密情報を出力しない
- [ ] ファイルアップロードを検証

### 9.2 リリース前

- [ ] 依存関係の脆弱性スキャン
- [ ] デバッグモードの無効化
- [ ] 不要なエンドポイントの削除
- [ ] エラーメッセージに内部情報を含まない

## 10. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |
