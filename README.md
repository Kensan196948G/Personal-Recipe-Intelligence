# Personal Recipe Intelligence (PRI)

個人向け料理レシピ収集・解析・管理システム

## 概要

Personal Recipe Intelligence (PRI) は、様々なソースからレシピを収集し、構造化データとして管理できる個人向けシステムです。

### 主な機能

- **Web スクレイピング**: 国内・海外のレシピサイトからレシピを抽出
- **OCR 解析**: 手書きレシピや雑誌の写真からテキスト抽出
- **自動翻訳**: DeepL API を使用した海外レシピの日本語化
- **データ正規化**: 材料名・分量の統一処理
- **WebUI**: 軽量な検索・閲覧インターフェース

### 対応レシピ取得元

| カテゴリ | 対応サイト |
|---------|-----------|
| 国内サイト | クックパッド, クラシル, デリッシュキッチン, Nadia 等 |
| 海外サイト | Allrecipes, BBC GoodFood, NYTimes Cooking 等 |
| 動画 | YouTube, Instagram Reels, TikTok |
| 画像 | 手書きレシピ, 雑誌, パッケージ裏面 |

## セットアップ

### 必要環境

- Python 3.11
- Node.js 20
- Bun (最新版)

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/Kensan196948G/Personal-Recipe-Intelligence.git
cd Personal-Recipe-Intelligence

# セットアップスクリプトを実行
./scripts/setup.sh
```

### 環境変数の設定

```bash
# .env.example をコピーして編集
cp .env.example .env

# DeepL API キーなどを設定
```

## ディレクトリ構成

```
personal-recipe-intelligence/
├── backend/           # Python API (FastAPI)
│   ├── api/           # エンドポイント
│   ├── models/        # SQLModel / Pydantic
│   ├── services/      # ビジネスロジック
│   ├── scraper/       # Web スクレイピング
│   ├── ocr/           # OCR 処理
│   └── translation/   # DeepL 翻訳
├── frontend/          # WebUI (Svelte)
├── config/            # 設定ファイル
├── data/              # SQLite / JSON 保存
├── docs/              # 仕様書
├── scripts/           # 自動化スクリプト
└── tests/             # 統合テスト
```

## 使用方法

### 開発サーバー起動

```bash
# API と UI を同時起動
./scripts/dev.sh
```

### テスト実行

```bash
./scripts/test.sh
```

### Lint チェック

```bash
./scripts/lint.sh
```

## API エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| GET | /api/v1/recipes | レシピ一覧取得 |
| GET | /api/v1/recipes/{id} | レシピ詳細取得 |
| POST | /api/v1/recipes | レシピ追加 |
| PUT | /api/v1/recipes/{id} | レシピ更新 |
| DELETE | /api/v1/recipes/{id} | レシピ削除 |
| POST | /api/v1/scrape | URL からレシピ抽出 |
| POST | /api/v1/ocr | 画像からレシピ抽出 |

## 技術スタック

### Backend
- Python 3.11
- FastAPI
- SQLModel / SQLAlchemy
- Alembic (マイグレーション)
- Pydantic (バリデーション)

### Frontend
- Svelte
- Bun

### インフラ
- SQLite (データベース)
- DeepL API (翻訳)

## ライセンス

MIT License

## 作者

Kensan196948G
