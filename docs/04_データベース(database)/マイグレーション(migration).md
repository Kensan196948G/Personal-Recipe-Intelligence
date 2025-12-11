# マイグレーション (Migration)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) のデータベースマイグレーション管理について定義する。

## 2. マイグレーションツール

- **ツール**: Alembic
- **設定ファイル**: `backend/alembic.ini`
- **マイグレーションディレクトリ**: `backend/alembic/`

## 3. ディレクトリ構造

```
backend/
├── alembic.ini
└── alembic/
    ├── env.py
    ├── script.py.mako
    └── versions/
        ├── 001_initial_schema.py
        ├── 002_add_translation_cache.py
        └── ...
```

## 4. 基本コマンド

### 4.1 マイグレーション作成

```bash
# 新規マイグレーション作成
cd backend
alembic revision -m "add new table"

# 自動生成（モデル変更を検出）
alembic revision --autogenerate -m "add new column"
```

### 4.2 マイグレーション実行

```bash
# 最新版まで適用
alembic upgrade head

# 1つ進める
alembic upgrade +1

# 特定バージョンまで
alembic upgrade <revision_id>
```

### 4.3 ロールバック

```bash
# 1つ戻す
alembic downgrade -1

# 初期状態に戻す
alembic downgrade base

# 特定バージョンまで
alembic downgrade <revision_id>
```

### 4.4 状態確認

```bash
# 現在のバージョン
alembic current

# 履歴表示
alembic history

# 保留中のマイグレーション
alembic heads
```

## 5. マイグレーションファイル

### 5.1 初期スキーマ

**ファイル名**: `001_initial_schema.py`

```python
"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-12-11
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # recipe テーブル
    op.create_table(
        'recipe',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('title_original', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('servings', sa.Integer(), nullable=True),
        sa.Column('prep_time_minutes', sa.Integer(), nullable=True),
        sa.Column('cook_time_minutes', sa.Integer(), nullable=True),
        sa.Column('image_path', sa.String(500), nullable=True),
        sa.Column('language', sa.String(10), default='ja'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
    )
    op.create_index('idx_recipe_title', 'recipe', ['title'])
    op.create_index('idx_recipe_created_at', 'recipe', ['created_at'])
    op.create_index('idx_recipe_is_deleted', 'recipe', ['is_deleted'])

    # ingredient テーブル
    op.create_table(
        'ingredient',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_normalized', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('idx_ingredient_normalized', 'ingredient', ['name_normalized'], unique=True)

    # recipe_ingredient テーブル
    op.create_table(
        'recipe_ingredient',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('recipe_id', sa.Integer(), sa.ForeignKey('recipe.id', ondelete='CASCADE')),
        sa.Column('ingredient_id', sa.Integer(), sa.ForeignKey('ingredient.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(20), nullable=True),
        sa.Column('note', sa.String(200), nullable=True),
        sa.Column('order_index', sa.Integer(), default=0),
    )
    op.create_index('idx_ri_recipe', 'recipe_ingredient', ['recipe_id'])

    # recipe_step テーブル
    op.create_table(
        'recipe_step',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('recipe_id', sa.Integer(), sa.ForeignKey('recipe.id', ondelete='CASCADE')),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('image_path', sa.String(500), nullable=True),
    )
    op.create_index('idx_rs_recipe', 'recipe_step', ['recipe_id'])

    # tag テーブル
    op.create_table(
        'tag',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('color', sa.String(7), default='#808080'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('idx_tag_name', 'tag', ['name'], unique=True)

    # recipe_tag テーブル
    op.create_table(
        'recipe_tag',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('recipe_id', sa.Integer(), sa.ForeignKey('recipe.id', ondelete='CASCADE')),
        sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tag.id', ondelete='CASCADE')),
    )
    op.create_index('idx_rt_recipe', 'recipe_tag', ['recipe_id'])
    op.create_index('idx_rt_tag', 'recipe_tag', ['tag_id'])

    # recipe_source テーブル
    op.create_table(
        'recipe_source',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('recipe_id', sa.Integer(), sa.ForeignKey('recipe.id', ondelete='CASCADE'), unique=True),
        sa.Column('source_type', sa.String(20), nullable=False),
        sa.Column('source_url', sa.String(2000), nullable=True),
        sa.Column('source_site', sa.String(100), nullable=True),
        sa.Column('scraped_at', sa.DateTime(), nullable=True),
    )

def downgrade():
    op.drop_table('recipe_source')
    op.drop_table('recipe_tag')
    op.drop_table('tag')
    op.drop_table('recipe_step')
    op.drop_table('recipe_ingredient')
    op.drop_table('ingredient')
    op.drop_table('recipe')
```

### 5.2 翻訳キャッシュ追加

**ファイル名**: `002_add_translation_cache.py`

```python
"""Add translation cache

Revision ID: 002
Revises: 001
Create Date: 2024-12-11
"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'

def upgrade():
    op.create_table(
        'translation_cache',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('source_text_hash', sa.String(64), nullable=False),
        sa.Column('source_text', sa.Text(), nullable=False),
        sa.Column('translated_text', sa.Text(), nullable=False),
        sa.Column('source_lang', sa.String(10), nullable=False),
        sa.Column('target_lang', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
    )
    op.create_index(
        'idx_translation_hash',
        'translation_cache',
        ['source_text_hash', 'source_lang', 'target_lang'],
        unique=True
    )

def downgrade():
    op.drop_table('translation_cache')
```

## 6. マイグレーション命名規則

```
<連番>_<説明>.py

例:
001_initial_schema.py
002_add_translation_cache.py
003_add_recipe_rating.py
004_add_user_preferences.py
```

## 7. 運用ルール

### 7.1 開発時

1. モデル変更時は必ずマイグレーションを作成
2. `--autogenerate` の結果は必ずレビュー
3. データ移行が必要な場合は `op.execute()` で SQL を実行

### 7.2 本番適用時

1. バックアップを取得
2. テスト環境で事前検証
3. マイグレーション実行
4. 動作確認

### 7.3 ロールバック時

1. 影響範囲を確認
2. ロールバック実行
3. データ復旧（必要に応じて）

## 8. トラブルシューティング

### 8.1 マイグレーション失敗時

```bash
# 現在の状態を確認
alembic current

# 手動でバージョンを設定
alembic stamp <revision_id>
```

### 8.2 コンフリクト時

```bash
# マージマイグレーション作成
alembic merge heads -m "merge migrations"
```

## 9. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |
