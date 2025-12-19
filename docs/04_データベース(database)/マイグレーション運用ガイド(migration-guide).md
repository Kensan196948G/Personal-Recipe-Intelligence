# Alembic マイグレーション運用ガイド

**Personal Recipe Intelligence - Database Migration Guide**

**最終更新**: 2025-12-19
**バージョン**: 1.0.0

---

## 📋 目次

1. [概要](#概要)
2. [環境セットアップ](#環境セットアップ)
3. [マイグレーション基本操作](#マイグレーション基本操作)
4. [マイグレーション作成](#マイグレーション作成)
5. [トラブルシューティング](#トラブルシューティング)
6. [ベストプラクティス](#ベストプラクティス)
7. [リファレンス](#リファレンス)

---

## 概要

### Alembicとは

Alembicは、SQLAlchemyベースのデータベーススキーママイグレーションツールです。
PRIプロジェクトでは、SQLModelを使用しているため、SQLModelのメタデータからAlembicが自動的にマイグレーションを生成します。

### 主な機能

- ✅ **スキーマバージョン管理** - データベーススキーマの変更履歴を管理
- ✅ **自動マイグレーション生成** - モデル定義から差分を自動検出
- ✅ **ロールバック** - 任意のバージョンへの戻し対応
- ✅ **SQLite対応** - batch操作で安全にスキーマ変更

---

## 環境セットアップ

### 前提条件

- Python 3.11+
- sqlite3
- git

### 1. 仮想環境のセットアップ

#### Ubuntu/Debian

```bash
# python3-venvパッケージのインストール
sudo apt update
sudo apt install python3.12-venv

# プロジェクトルートで仮想環境を作成
cd /path/to/Personal-Recipe-Intelligence
python3 -m venv .venv

# 仮想環境を有効化
source .venv/bin/activate

# 依存パッケージのインストール
pip install --upgrade pip
pip install -r backend/requirements.txt
```

#### 仮想環境の確認

```bash
# 正常にインストールされているか確認
python -c "import alembic; print(alembic.__version__)"
# 出力例: 1.13.0
```

### 2. Alembic設定の確認

```bash
# alembic.ini が存在することを確認
ls -la alembic.ini

# alembic/versions/ ディレクトリを確認
ls -la alembic/versions/
```

### 3. データベース接続設定

**alembic.ini** (既に設定済み):
```ini
sqlalchemy.url = sqlite:///./data/pri.db
```

---

## マイグレーション基本操作

### 現在のマイグレーション状態を確認

```bash
# 仮想環境を有効化
source .venv/bin/activate

# プロジェクトルートから実行
cd /path/to/Personal-Recipe-Intelligence

# 現在のバージョンを表示
alembic current

# 詳細表示
alembic current -v
```

**期待される出力**:
```
d858e3540dc2 (head)
```

### マイグレーション履歴の確認

```bash
# すべてのマイグレーションを表示
alembic history

# 詳細履歴
alembic history -v
```

### 最新バージョンへアップグレード

```bash
# 最新バージョンまでマイグレーション実行
alembic upgrade head

# 成功時の出力例:
# INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
# INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
# INFO  [alembic.runtime.migration] Running upgrade  -> d858e3540dc2, Initial migration - create all tables
```

### 特定のバージョンへアップグレード

```bash
# リビジョンIDを指定
alembic upgrade d858e3540dc2

# 相対的な指定（1つ先へ）
alembic upgrade +1
```

### ダウングレード（ロールバック）

```bash
# 1つ前のバージョンへ戻す
alembic downgrade -1

# 特定のバージョンへ戻す
alembic downgrade d858e3540dc2

# 初期状態へ戻す（すべてのマイグレーションを取り消し）
alembic downgrade base
```

---

## マイグレーション作成

### 1. モデルの変更

例: Recipeモデルに新しいフィールドを追加

**backend/models/recipe.py**:
```python
class Recipe(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str | None = None
    servings: int | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None

    # 🆕 新しいフィールド
    difficulty: str | None = Field(default="medium")  # easy, medium, hard
    calories: int | None = None

    source_url: str | None = None
    source_type: str = Field(default="manual")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

### 2. マイグレーションファイルの自動生成

```bash
# 仮想環境を有効化
source .venv/bin/activate

# プロジェクトルートから実行
cd /path/to/Personal-Recipe-Intelligence

# マイグレーションを自動生成
alembic revision --autogenerate -m "Add difficulty and calories to Recipe"
```

**生成されるファイル**:
```
alembic/versions/abc123def456_add_difficulty_and_calories_to_recipe.py
```

### 3. 生成されたマイグレーションファイルの確認

```python
"""Add difficulty and calories to Recipe

Revision ID: abc123def456
Revises: d858e3540dc2
Create Date: 2025-12-19 10:30:00.123456

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123def456'
down_revision = 'd858e3540dc2'

def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.add_column(sa.Column('difficulty', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('calories', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.drop_column('calories')
        batch_op.drop_column('difficulty')
```

### 4. マイグレーションの実行

```bash
# テスト環境で実行（推奨）
cp data/pri.db data/pri.db.backup
alembic upgrade head

# 問題がなければ本番適用
```

### 5. ロールバックテスト

```bash
# ダウングレードして問題ないか確認
alembic downgrade -1

# 再度アップグレード
alembic upgrade head
```

---

## トラブルシューティング

### エラー: `alembic: command not found`

**原因**: 仮想環境が有効化されていない、またはalembicがインストールされていない

**解決**:
```bash
# 仮想環境を有効化
source .venv/bin/activate

# alembicがインストールされているか確認
pip list | grep alembic

# インストールされていない場合
pip install alembic>=1.13.0
```

### エラー: `Can't locate revision identified by 'XXXXX'`

**原因**: マイグレーションファイルが見つからない、またはデータベースの状態が不整合

**解決**:
```bash
# 1. マイグレーション履歴を確認
alembic history

# 2. データベースの alembic_version テーブルを確認
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('data/pri.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM alembic_version")
print(cursor.fetchall())
conn.close()
EOF

# 3. 手動で修正（最終手段）
alembic stamp head
```

### エラー: `Target database is not up to date`

**原因**: データベースが最新のマイグレーションまで適用されていない

**解決**:
```bash
# 現在のバージョンを確認
alembic current

# 最新まで適用
alembic upgrade head
```

### SQLiteで `batch_alter_table` エラー

**原因**: SQLiteは一部のALTER TABLE操作に制限がある

**解決**: env.pyで `render_as_batch=True` が設定されていることを確認（既に設定済み）

```python
# alembic/env.py
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    render_as_batch=True,  # ← 重要
)
```

---

## ベストプラクティス

### 1. マイグレーション作成前の確認事項

- [ ] モデル変更が正しく定義されているか
- [ ] テストコードを書いているか
- [ ] データベースのバックアップを取得しているか

### 2. マイグレーション命名規則

```bash
# 良い例
alembic revision --autogenerate -m "Add user_id to Recipe"
alembic revision --autogenerate -m "Create nutrition_info table"
alembic revision --autogenerate -m "Add index on recipe.created_at"

# 悪い例（避ける）
alembic revision --autogenerate -m "update"
alembic revision --autogenerate -m "fix"
```

### 3. マイグレーション実行前

```bash
# 1. データベースバックアップ
cp data/pri.db data/pri.db.$(date +%Y%m%d_%H%M%S).backup

# 2. 現在のバージョン確認
alembic current

# 3. 適用予定のマイグレーション確認
alembic upgrade head --sql  # SQL文のみ表示（実行しない）

# 4. 実行
alembic upgrade head
```

### 4. 本番環境での注意事項

⚠️ **本番環境では特に慎重に**:

1. **必ずバックアップを取得**
   ```bash
   cp data/pri.db data/pri.db.backup
   ```

2. **ダウンタイムを考慮**
   - マイグレーション中はアプリを停止
   - ユーザーに事前通知

3. **ロールバック計画**
   - ダウングレード手順を事前にテスト

4. **段階的適用**
   - 一度に複数のマイグレーションを適用しない
   - 1つずつ確認しながら進める

### 5. gitでのマイグレーション管理

```bash
# マイグレーションファイルは必ずコミット
git add alembic/versions/abc123def456_*.py
git commit -m "feat(db): add difficulty and calories to Recipe

- Add difficulty field (easy/medium/hard)
- Add calories field for nutrition tracking
- Migration: abc123def456
"
```

---

## リファレンス

### よく使うAlembicコマンド一覧

| コマンド | 説明 |
|---------|------|
| `alembic current` | 現在のバージョンを表示 |
| `alembic history` | マイグレーション履歴を表示 |
| `alembic upgrade head` | 最新バージョンまでアップグレード |
| `alembic upgrade +1` | 1つ先のバージョンへアップグレード |
| `alembic downgrade -1` | 1つ前のバージョンへダウングレード |
| `alembic downgrade base` | 初期状態へロールバック |
| `alembic revision --autogenerate -m "message"` | マイグレーション自動生成 |
| `alembic revision -m "message"` | 空のマイグレーション作成 |
| `alembic stamp head` | データベースを最新バージョンとしてマーク（実行なし） |
| `alembic show <revision>` | 特定のリビジョンの詳細を表示 |

### ファイル構成

```
Personal-Recipe-Intelligence/
├── alembic.ini                 # Alembic設定ファイル
├── alembic/
│   ├── env.py                 # 環境設定・モデルインポート
│   ├── script.py.mako         # マイグレーションテンプレート
│   ├── README                 # Alembic README
│   └── versions/              # マイグレーションファイル
│       └── d858e3540dc2_initial_migration_create_all_tables.py
├── backend/
│   └── models/
│       └── recipe.py          # モデル定義
└── data/
    └── pri.db                 # SQLiteデータベース
```

### 関連ドキュメント

- [Alembic公式ドキュメント](https://alembic.sqlalchemy.org/)
- [SQLModel公式ドキュメント](https://sqlmodel.tiangolo.com/)
- [PRIデータベース設計](./テーブル定義書(table-definitions).md)
- [PRIマイグレーション履歴](./migration.md)

---

## セットアップスクリプト

便利なセットアップスクリプトを `scripts/setup-alembic.sh` に用意しています。

```bash
# 初回セットアップ
./scripts/setup-alembic.sh

# 使用方法が表示されます
```

---

## 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2025-12-19 | 1.0.0 | 初版作成 |

---

**作成者**: Claude Code DevAPIAgent
**レビュー**: PlannerAgent, QaAgent
