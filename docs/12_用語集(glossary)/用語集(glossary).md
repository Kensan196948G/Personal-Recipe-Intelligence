# 用語集 (Glossary)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) プロジェクトで使用される用語を定義する。

## 2. プロジェクト用語

### A

#### Agent
ClaudeCode の SubAgent のこと。特定のタスクを担当する自律的なモジュール。

#### API (Application Programming Interface)
アプリケーション間でデータをやり取りするためのインターフェース。本プロジェクトでは FastAPI で実装。

### B

#### Bun
高速な JavaScript ランタイム兼パッケージマネージャー。フロントエンドの開発に使用。

### C

#### CLAUDE.md
ClaudeCode の開発ルールを定義したファイル。プロジェクト固有の設定を記述。

#### ClaudeCode
Anthropic が提供する AI 開発アシスタント。本プロジェクトの開発支援に使用。

#### CRUD
Create, Read, Update, Delete の略。データ操作の基本機能。

### D

#### DeepL
機械翻訳サービス。海外レシピの日本語翻訳に使用。

#### DOM (Document Object Model)
HTML/XML ドキュメントの構造を表現するモデル。スクレイピングで解析対象。

### E

#### Endpoint
API のアクセスポイント。例: `/api/v1/recipes`

### F

#### FastAPI
Python の高速 Web フレームワーク。バックエンド API の実装に使用。

### H

#### Hook
特定のイベント発生時に実行されるコールバック関数。ClaudeCode の連携処理に使用。

#### HMR (Hot Module Replacement)
開発時にコード変更を即座に反映する機能。

### J

#### JSON (JavaScript Object Notation)
軽量なデータ交換フォーマット。API のリクエスト/レスポンスに使用。

#### JSON-LD
構造化データを表現する JSON 形式。レシピサイトの構造化データに使用。

### M

#### MCP (Model Context Protocol)
ClaudeCode が外部ツール（ブラウザ、ファイルシステム等）と連携するためのプロトコル。

#### Migration
データベーススキーマの変更を管理する仕組み。Alembic で実装。

### N

#### Normalization
データの正規化。材料名の表記統一など。

### O

#### OCR (Optical Character Recognition)
光学文字認識。画像からテキストを抽出する技術。

#### ORM (Object-Relational Mapping)
オブジェクトとリレーショナルデータベースを対応付ける技術。SQLModel で実装。

### P

#### PRI
Personal Recipe Intelligence の略。本プロジェクトの名称。

#### Pydantic
Python のデータバリデーションライブラリ。API のリクエスト/レスポンス検証に使用。

### R

#### REST (Representational State Transfer)
Web API の設計スタイル。本プロジェクトの API 設計に採用。

#### robots.txt
Web サイトがクローラーに対して指示を与えるファイル。スクレイピング時に遵守。

### S

#### Schema
データ構造の定義。Pydantic モデルまたはデータベーステーブル定義。

#### Scraping
Web ページからデータを自動抽出すること。

#### SQLite
軽量なファイルベースのデータベース。本プロジェクトのデータ保存に使用。

#### SQLModel
SQLAlchemy + Pydantic を統合した ORM ライブラリ。

#### Store
Svelte の状態管理機構。アプリケーション状態の管理に使用。

#### SubAgent
ClaudeCode の Agent のこと。タスクを分担して実行。

#### Svelte
コンパイル時に最適化される軽量 UI フレームワーク。フロントエンドに使用。

### T

#### Tag
レシピに付けるラベル。分類・検索に使用。

### U

#### Uvicorn
高速な ASGI サーバー。FastAPI アプリケーションの実行に使用。

### V

#### Vite
高速な開発サーバー兼ビルドツール。フロントエンド開発に使用。

#### Vision API
画像認識 API。OCR 処理に使用。

### W

#### WebUI
Web ベースのユーザーインターフェース。

## 3. レシピ関連用語

### 調理用語

| 用語 | 説明 |
|------|------|
| 下準備 | 調理前の準備作業 |
| 調理時間 | 実際に調理にかかる時間 |
| 分量 | 材料の量（人数分） |

### 単位

| 英語 | 日本語 | 換算 |
|------|--------|------|
| cup | カップ | 240ml |
| tbsp | 大さじ | 15ml |
| tsp | 小さじ | 5ml |
| oz | オンス | 28.35g |
| lb | ポンド | 453.6g |

## 4. 技術用語

### HTTP ステータスコード

| コード | 意味 |
|--------|------|
| 200 | OK - 成功 |
| 201 | Created - 作成成功 |
| 400 | Bad Request - リクエスト不正 |
| 404 | Not Found - 未発見 |
| 422 | Unprocessable Entity - 処理不可 |
| 500 | Internal Server Error - サーバーエラー |

### データベース用語

| 用語 | 説明 |
|------|------|
| PK (Primary Key) | 主キー |
| FK (Foreign Key) | 外部キー |
| Index | インデックス（検索高速化） |
| Transaction | トランザクション |
| Migration | スキーマ変更管理 |

## 5. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |
