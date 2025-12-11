# テーブル定義書 (Table Definitions)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) のデータベーステーブル定義を詳細に記述する。

## 2. データベース情報

- **DBMS**: SQLite 3
- **文字コード**: UTF-8
- **照合順序**: NOCASE

## 3. テーブル定義

### 3.1 recipe（レシピ）

**概要**: レシピの基本情報を格納

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| title | VARCHAR(200) | NO | - | レシピタイトル |
| title_original | VARCHAR(200) | YES | NULL | 原文タイトル（翻訳前） |
| description | TEXT | YES | NULL | 説明 |
| servings | INTEGER | YES | NULL | 分量（人数） |
| prep_time_minutes | INTEGER | YES | NULL | 下準備時間（分） |
| cook_time_minutes | INTEGER | YES | NULL | 調理時間（分） |
| image_path | VARCHAR(500) | YES | NULL | 画像パス |
| language | VARCHAR(10) | YES | 'ja' | 言語コード |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | 更新日時 |
| is_deleted | BOOLEAN | NO | FALSE | 削除フラグ |

**制約**
```sql
PRIMARY KEY (id)
CHECK (servings > 0 AND servings <= 100)
CHECK (prep_time_minutes >= 0 AND prep_time_minutes <= 1440)
CHECK (cook_time_minutes >= 0 AND cook_time_minutes <= 1440)
```

**インデックス**
```sql
CREATE INDEX idx_recipe_title ON recipe(title);
CREATE INDEX idx_recipe_created_at ON recipe(created_at DESC);
CREATE INDEX idx_recipe_is_deleted ON recipe(is_deleted);
```

---

### 3.2 ingredient（材料マスタ）

**概要**: 材料の正規化マスタ

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| name | VARCHAR(100) | NO | - | 材料名 |
| name_normalized | VARCHAR(100) | NO | - | 正規化名（ひらがな） |
| category | VARCHAR(50) | YES | NULL | カテゴリ（野菜、肉等） |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 作成日時 |

**制約**
```sql
PRIMARY KEY (id)
UNIQUE (name_normalized)
```

**インデックス**
```sql
CREATE UNIQUE INDEX idx_ingredient_normalized ON ingredient(name_normalized);
CREATE INDEX idx_ingredient_category ON ingredient(category);
```

---

### 3.3 recipe_ingredient（レシピ材料）

**概要**: レシピと材料の中間テーブル

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| recipe_id | INTEGER | NO | - | レシピID |
| ingredient_id | INTEGER | YES | NULL | 材料ID（マスタ） |
| name | VARCHAR(100) | NO | - | 材料名（入力値） |
| amount | REAL | YES | NULL | 分量 |
| unit | VARCHAR(20) | YES | NULL | 単位 |
| note | VARCHAR(200) | YES | NULL | 備考 |
| order_index | INTEGER | NO | 0 | 表示順 |

**制約**
```sql
PRIMARY KEY (id)
FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE
FOREIGN KEY (ingredient_id) REFERENCES ingredient(id) ON DELETE SET NULL
```

**インデックス**
```sql
CREATE INDEX idx_recipe_ingredient_recipe ON recipe_ingredient(recipe_id);
CREATE INDEX idx_recipe_ingredient_ingredient ON recipe_ingredient(ingredient_id);
```

---

### 3.4 recipe_step（レシピ手順）

**概要**: レシピの調理手順

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| recipe_id | INTEGER | NO | - | レシピID |
| step_number | INTEGER | NO | - | 手順番号 |
| description | TEXT | NO | - | 手順内容 |
| image_path | VARCHAR(500) | YES | NULL | 手順画像パス |

**制約**
```sql
PRIMARY KEY (id)
FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE
UNIQUE (recipe_id, step_number)
CHECK (step_number > 0)
```

**インデックス**
```sql
CREATE INDEX idx_recipe_step_recipe ON recipe_step(recipe_id);
```

---

### 3.5 tag（タグ）

**概要**: タグマスタ

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| name | VARCHAR(50) | NO | - | タグ名 |
| category | VARCHAR(50) | YES | NULL | カテゴリ |
| color | VARCHAR(7) | YES | '#808080' | 表示色（HEX） |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 作成日時 |

**制約**
```sql
PRIMARY KEY (id)
UNIQUE (name)
```

**インデックス**
```sql
CREATE UNIQUE INDEX idx_tag_name ON tag(name);
CREATE INDEX idx_tag_category ON tag(category);
```

---

### 3.6 recipe_tag（レシピタグ）

**概要**: レシピとタグの中間テーブル

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| recipe_id | INTEGER | NO | - | レシピID |
| tag_id | INTEGER | NO | - | タグID |

**制約**
```sql
PRIMARY KEY (id)
FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE
FOREIGN KEY (tag_id) REFERENCES tag(id) ON DELETE CASCADE
UNIQUE (recipe_id, tag_id)
```

**インデックス**
```sql
CREATE INDEX idx_recipe_tag_recipe ON recipe_tag(recipe_id);
CREATE INDEX idx_recipe_tag_tag ON recipe_tag(tag_id);
```

---

### 3.7 recipe_source（レシピソース）

**概要**: レシピの取得元情報

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| recipe_id | INTEGER | NO | - | レシピID |
| source_type | VARCHAR(20) | NO | - | ソース種別 |
| source_url | VARCHAR(2000) | YES | NULL | URL |
| source_site | VARCHAR(100) | YES | NULL | サイト名 |
| scraped_at | DATETIME | YES | NULL | 取得日時 |

**source_type 値**
- `manual`: 手動入力
- `scrape`: Webスクレイピング
- `ocr`: OCR

**制約**
```sql
PRIMARY KEY (id)
FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE
UNIQUE (recipe_id)
CHECK (source_type IN ('manual', 'scrape', 'ocr'))
```

---

### 3.8 translation_cache（翻訳キャッシュ）

**概要**: 翻訳結果のキャッシュ

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| source_text_hash | VARCHAR(64) | NO | - | 原文ハッシュ |
| source_text | TEXT | NO | - | 原文 |
| translated_text | TEXT | NO | - | 翻訳文 |
| source_lang | VARCHAR(10) | NO | - | 原文言語 |
| target_lang | VARCHAR(10) | NO | - | 翻訳先言語 |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 作成日時 |
| expires_at | DATETIME | YES | NULL | 有効期限 |

**制約**
```sql
PRIMARY KEY (id)
UNIQUE (source_text_hash, source_lang, target_lang)
```

**インデックス**
```sql
CREATE UNIQUE INDEX idx_translation_hash ON translation_cache(source_text_hash, source_lang, target_lang);
CREATE INDEX idx_translation_expires ON translation_cache(expires_at);
```

## 4. 初期データ

### 4.1 タグ初期データ

```sql
INSERT INTO tag (name, category, color) VALUES
  ('和食', 'ジャンル', '#FF6B35'),
  ('洋食', 'ジャンル', '#4CAF50'),
  ('中華', 'ジャンル', '#F44336'),
  ('簡単', '難易度', '#2196F3'),
  ('本格', '難易度', '#9C27B0'),
  ('時短', '特徴', '#FF9800'),
  ('ヘルシー', '特徴', '#8BC34A'),
  ('おもてなし', '用途', '#E91E63');
```

## 5. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |
