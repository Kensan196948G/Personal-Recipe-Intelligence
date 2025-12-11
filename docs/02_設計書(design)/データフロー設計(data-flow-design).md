# データフロー設計 (Data Flow Design)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) におけるデータの流れを定義する。

## 2. 全体データフロー

```mermaid
flowchart TD
    subgraph Input["入力ソース"]
        A1[Webサイト]
        A2[画像/OCR]
        A3[手動入力]
    end

    subgraph Processing["処理層"]
        B1[ScraperAgent]
        B2[OcrAgent]
        B3[TranslationAgent]
        B4[CleanerAgent]
    end

    subgraph Storage["保存層"]
        C1[(SQLite DB)]
        C2[/画像ファイル/]
    end

    subgraph Output["出力"]
        D1[WebUI]
        D2[API Response]
        D3[Export File]
    end

    A1 --> B1
    A2 --> B2
    A3 --> B4
    B1 --> B3
    B2 --> B3
    B3 --> B4
    B4 --> C1
    A2 --> C2
    C1 --> D1
    C1 --> D2
    C1 --> D3
```

## 3. 詳細データフロー

### 3.1 Webスクレイピングフロー

```mermaid
sequenceDiagram
    participant U as User
    participant UI as WebUI
    participant API as FastAPI
    participant SC as ScraperAgent
    participant MCP as Browser MCP
    participant TR as TranslationAgent
    participant CL as CleanerAgent
    participant DB as SQLite

    U->>UI: URL入力
    UI->>API: POST /scrape {url}
    API->>SC: scrape(url)
    SC->>MCP: acquireMCP('browser')
    MCP-->>SC: OK
    SC->>SC: fetch HTML
    SC->>SC: parse DOM
    SC->>SC: extract data
    SC->>MCP: releaseMCP()
    SC-->>API: raw_recipe_data

    alt language != 'ja'
        API->>TR: translate(data)
        TR->>TR: DeepL API call
        TR-->>API: translated_data
    end

    API->>CL: clean(data)
    CL->>CL: normalize ingredients
    CL->>CL: normalize steps
    CL-->>API: cleaned_data

    API->>DB: INSERT recipe
    DB-->>API: recipe_id
    API-->>UI: {status: 'ok', data: recipe}
    UI-->>U: 表示
```

### 3.2 OCRフロー

```mermaid
sequenceDiagram
    participant U as User
    participant UI as WebUI
    participant API as FastAPI
    participant FS as FileSystem
    participant OCR as OcrAgent
    participant MCP as Filesystem MCP
    participant CL as CleanerAgent
    participant DB as SQLite

    U->>UI: 画像選択
    UI->>API: POST /ocr (multipart)
    API->>FS: save image
    FS-->>API: image_path

    API->>OCR: extract(image_path)
    OCR->>MCP: acquireMCP('filesystem')
    MCP-->>OCR: OK
    OCR->>OCR: load image
    OCR->>OCR: Vision API call
    OCR->>OCR: parse text
    OCR->>MCP: releaseMCP()
    OCR-->>API: extracted_data

    API->>CL: clean(data)
    CL-->>API: cleaned_data

    API->>DB: INSERT recipe
    DB-->>API: recipe_id
    API-->>UI: {status: 'ok', data: recipe}
    UI-->>U: 表示
```

### 3.3 CRUD操作フロー

```mermaid
sequenceDiagram
    participant U as User
    participant UI as WebUI
    participant API as FastAPI
    participant SVC as RecipeService
    participant DB as SQLite

    Note over U,DB: CREATE
    U->>UI: フォーム入力
    UI->>API: POST /recipes
    API->>SVC: create(data)
    SVC->>DB: INSERT
    DB-->>SVC: recipe_id
    SVC-->>API: recipe
    API-->>UI: response
    UI-->>U: 完了表示

    Note over U,DB: READ
    U->>UI: レシピ選択
    UI->>API: GET /recipes/{id}
    API->>SVC: get(id)
    SVC->>DB: SELECT
    DB-->>SVC: row
    SVC-->>API: recipe
    API-->>UI: response
    UI-->>U: 詳細表示

    Note over U,DB: UPDATE
    U->>UI: 編集・保存
    UI->>API: PUT /recipes/{id}
    API->>SVC: update(id, data)
    SVC->>DB: UPDATE
    DB-->>SVC: OK
    SVC-->>API: recipe
    API-->>UI: response
    UI-->>U: 完了表示

    Note over U,DB: DELETE
    U->>UI: 削除ボタン
    UI->>API: DELETE /recipes/{id}
    API->>SVC: delete(id)
    SVC->>DB: UPDATE is_deleted=true
    DB-->>SVC: OK
    SVC-->>API: OK
    API-->>UI: response
    UI-->>U: 完了表示
```

## 4. データ変換

### 4.1 スクレイピングデータ変換

```
[HTML] --> [Raw Data] --> [Translated] --> [Normalized] --> [DB Record]

例:
HTML:
<h1>Chicken Curry</h1>
<li>2 cups rice</li>

Raw Data:
{
  "title": "Chicken Curry",
  "ingredients": ["2 cups rice"]
}

Translated:
{
  "title": "チキンカレー",
  "ingredients": ["2カップ ご飯"]
}

Normalized:
{
  "title": "チキンカレー",
  "ingredients": [
    {
      "name": "ご飯",
      "name_normalized": "ごはん",
      "amount": 480,
      "unit": "ml"
    }
  ]
}
```

### 4.2 OCRデータ変換

```
[Image] --> [Raw Text] --> [Structured] --> [Normalized] --> [DB Record]

例:
Raw Text:
"カレーライス
材料（2人分）
玉ねぎ 1個
にんじん 1/2本
..."

Structured:
{
  "title": "カレーライス",
  "servings": 2,
  "ingredients": [
    "玉ねぎ 1個",
    "にんじん 1/2本"
  ]
}

Normalized:
{
  "title": "カレーライス",
  "servings": 2,
  "ingredients": [
    {"name": "たまねぎ", "amount": 1, "unit": "個"},
    {"name": "にんじん", "amount": 0.5, "unit": "本"}
  ]
}
```

## 5. エラーハンドリング

### 5.1 エラーフロー

```mermaid
flowchart TD
    A[リクエスト] --> B{バリデーション}
    B -->|NG| C[400 Bad Request]
    B -->|OK| D{認証}
    D -->|NG| E[401 Unauthorized]
    D -->|OK| F{処理}
    F -->|エラー| G{エラー種別}
    G -->|NotFound| H[404 Not Found]
    G -->|Conflict| I[409 Conflict]
    G -->|Internal| J[500 Internal Error]
    F -->|成功| K[200 OK]
```

### 5.2 リトライフロー

```mermaid
flowchart TD
    A[外部API呼び出し] --> B{成功?}
    B -->|Yes| C[結果返却]
    B -->|No| D{リトライ回数}
    D -->|< 3回| E[待機]
    E --> A
    D -->|>= 3回| F[エラー返却]
```

## 6. キャッシュフロー

### 6.1 翻訳キャッシュ

```mermaid
flowchart TD
    A[翻訳リクエスト] --> B{キャッシュ確認}
    B -->|Hit| C[キャッシュ返却]
    B -->|Miss| D[DeepL API呼び出し]
    D --> E[結果をキャッシュ]
    E --> F[結果返却]
```

### 6.2 キャッシュ戦略

| データ種別 | TTL | 保存先 |
|-----------|-----|--------|
| 翻訳結果 | 30日 | SQLite |
| サイト構造 | 7日 | メモリ |
| 検索結果 | 5分 | メモリ |

## 7. バッチ処理フロー

### 7.1 日次バックアップ

```mermaid
flowchart TD
    A[スケジュール起動] --> B[DBダンプ]
    B --> C[ファイル圧縮]
    C --> D[バックアップ先へコピー]
    D --> E[古いバックアップ削除]
    E --> F[完了ログ記録]
```

## 8. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |
