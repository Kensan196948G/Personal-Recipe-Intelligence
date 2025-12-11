# テストケース (Test Cases)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) の詳細なテストケースを定義する。

## 2. バックエンドテストケース

### 2.1 レシピAPI テスト

#### TC-001: レシピ一覧取得

```python
# tests/test_recipes.py

def test_get_recipes_empty(client, db_session):
    """レシピがない場合は空配列を返す"""
    response = client.get("/api/v1/recipes")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["data"]["items"] == []
    assert data["data"]["total"] == 0

def test_get_recipes_with_data(client, db_session, sample_recipes):
    """レシピがある場合は一覧を返す"""
    response = client.get("/api/v1/recipes")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert len(data["data"]["items"]) == len(sample_recipes)

def test_get_recipes_pagination(client, db_session, many_recipes):
    """ページネーションが正しく動作する"""
    response = client.get("/api/v1/recipes?page=2&per_page=10")

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["page"] == 2
    assert len(data["data"]["items"]) <= 10
```

#### TC-002: レシピ詳細取得

```python
def test_get_recipe_by_id(client, db_session, sample_recipe):
    """IDでレシピを取得できる"""
    response = client.get(f"/api/v1/recipes/{sample_recipe.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["id"] == sample_recipe.id
    assert data["data"]["title"] == sample_recipe.title

def test_get_recipe_not_found(client, db_session):
    """存在しないIDは404を返す"""
    response = client.get("/api/v1/recipes/9999")

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "NOT_FOUND"

def test_get_deleted_recipe(client, db_session, deleted_recipe):
    """削除済みレシピは404を返す"""
    response = client.get(f"/api/v1/recipes/{deleted_recipe.id}")

    assert response.status_code == 404
```

#### TC-003: レシピ作成

```python
def test_create_recipe_success(client, db_session):
    """正常なデータでレシピを作成できる"""
    payload = {
        "title": "テストレシピ",
        "description": "テスト用のレシピです",
        "servings": 4,
        "ingredients": [
            {"name": "たまねぎ", "amount": 2, "unit": "個"}
        ],
        "steps": [
            {"description": "たまねぎを切る"}
        ]
    }
    response = client.post("/api/v1/recipes", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["data"]["title"] == "テストレシピ"
    assert len(data["data"]["ingredients"]) == 1

def test_create_recipe_missing_title(client, db_session):
    """タイトルがない場合はエラー"""
    payload = {
        "description": "説明のみ",
        "ingredients": [{"name": "材料"}],
        "steps": [{"description": "手順"}]
    }
    response = client.post("/api/v1/recipes", json=payload)

    assert response.status_code == 422

def test_create_recipe_no_ingredients(client, db_session):
    """材料がない場合はエラー"""
    payload = {
        "title": "テスト",
        "ingredients": [],
        "steps": [{"description": "手順"}]
    }
    response = client.post("/api/v1/recipes", json=payload)

    assert response.status_code == 422
```

#### TC-004: レシピ更新

```python
def test_update_recipe(client, db_session, sample_recipe):
    """レシピを更新できる"""
    payload = {
        "title": "更新後のタイトル",
        "servings": 6
    }
    response = client.put(f"/api/v1/recipes/{sample_recipe.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["title"] == "更新後のタイトル"
    assert data["data"]["servings"] == 6

def test_update_recipe_not_found(client, db_session):
    """存在しないレシピの更新は404"""
    payload = {"title": "更新"}
    response = client.put("/api/v1/recipes/9999", json=payload)

    assert response.status_code == 404
```

#### TC-005: レシピ削除

```python
def test_delete_recipe(client, db_session, sample_recipe):
    """レシピを削除できる（論理削除）"""
    response = client.delete(f"/api/v1/recipes/{sample_recipe.id}")

    assert response.status_code == 204

    # 削除後は取得できない
    get_response = client.get(f"/api/v1/recipes/{sample_recipe.id}")
    assert get_response.status_code == 404
```

### 2.2 スクレイピングAPI テスト

```python
# tests/test_scrape.py

def test_scrape_cookpad(client, mock_httpx):
    """クックパッドのURLからスクレイピングできる"""
    mock_httpx.get.return_value = Mock(
        text="<html>...</html>",
        raise_for_status=Mock()
    )

    payload = {"url": "https://cookpad.com/recipe/12345"}
    response = client.post("/api/v1/scrape", json=payload)

    assert response.status_code == 201

def test_scrape_unsupported_site(client):
    """非対応サイトはエラー"""
    payload = {"url": "https://unknown-site.com/recipe"}
    response = client.post("/api/v1/scrape", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "SITE_NOT_SUPPORTED"

def test_scrape_invalid_url(client):
    """不正なURLはエラー"""
    payload = {"url": "not-a-url"}
    response = client.post("/api/v1/scrape", json=payload)

    assert response.status_code == 400

def test_get_supported_sites(client):
    """対応サイト一覧を取得できる"""
    response = client.get("/api/v1/scrape/supported")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]["sites"]) > 0
```

### 2.3 OCR API テスト

```python
# tests/test_ocr.py
import io

def test_ocr_valid_image(client, mock_vision_api):
    """有効な画像からテキスト抽出できる"""
    # テスト用画像を作成
    image_data = create_test_image()

    response = client.post(
        "/api/v1/ocr",
        files={"image": ("recipe.jpg", image_data, "image/jpeg")}
    )

    assert response.status_code == 201

def test_ocr_invalid_file_type(client):
    """無効なファイル形式はエラー"""
    response = client.post(
        "/api/v1/ocr",
        files={"image": ("file.txt", b"text content", "text/plain")}
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_FILE"

def test_ocr_file_too_large(client):
    """ファイルサイズ超過はエラー"""
    large_data = b"x" * (11 * 1024 * 1024)  # 11MB

    response = client.post(
        "/api/v1/ocr",
        files={"image": ("large.jpg", large_data, "image/jpeg")}
    )

    assert response.status_code == 413
```

### 2.4 サービステスト

```python
# tests/test_services.py

class TestCleanerService:
    def test_normalize_ingredient_name(self):
        """材料名を正規化できる"""
        service = CleanerService()
        result = service._clean_ingredient("玉ねぎ 2個")

        assert result["name_normalized"] == "たまねぎ"
        assert result["amount"] == 2
        assert result["unit"] == "個"

    def test_parse_fraction(self):
        """分数をパースできる"""
        service = CleanerService()

        assert service._parse_fraction("½") == 0.5
        assert service._parse_fraction("2") == 2.0
        assert service._parse_fraction("1.5") == 1.5

class TestTranslateService:
    def test_translate_with_cache(self, db_session, mock_deepl):
        """キャッシュがある場合はAPIを呼ばない"""
        service = TranslateService(db_session, "api_key")

        # 最初の呼び出し
        result1 = service.translate("Hello")
        assert mock_deepl.call_count == 1

        # 2回目はキャッシュから
        result2 = service.translate("Hello")
        assert mock_deepl.call_count == 1
        assert result1 == result2
```

## 3. フロントエンドテストケース

### 3.1 コンポーネントテスト

```javascript
// tests/RecipeCard.test.js
import { render, fireEvent } from '@testing-library/svelte';
import RecipeCard from '../src/components/recipe/RecipeCard.svelte';

describe('RecipeCard', () => {
  const mockRecipe = {
    id: 1,
    title: 'テストレシピ',
    cook_time_minutes: 30,
    servings: 4,
    tags: [{ name: '和食' }]
  };

  test('レシピタイトルを表示する', () => {
    const { getByText } = render(RecipeCard, { props: { recipe: mockRecipe } });
    expect(getByText('テストレシピ')).toBeInTheDocument();
  });

  test('調理時間を表示する', () => {
    const { getByText } = render(RecipeCard, { props: { recipe: mockRecipe } });
    expect(getByText('30分')).toBeInTheDocument();
  });

  test('タグを表示する', () => {
    const { getByText } = render(RecipeCard, { props: { recipe: mockRecipe } });
    expect(getByText('和食')).toBeInTheDocument();
  });

  test('クリックでイベント発火', async () => {
    const { component, container } = render(RecipeCard, { props: { recipe: mockRecipe } });
    const mockFn = vi.fn();
    component.$on('click', mockFn);

    await fireEvent.click(container.querySelector('.recipe-card'));
    expect(mockFn).toHaveBeenCalled();
  });
});
```

### 3.2 ストアテスト

```javascript
// tests/recipes.store.test.js
import { get } from 'svelte/store';
import { recipeStore } from '../src/stores/recipes';

describe('recipeStore', () => {
  beforeEach(() => {
    recipeStore.set([]);
  });

  test('レシピを追加できる', () => {
    const recipe = { id: 1, title: 'テスト' };
    recipeStore.add(recipe);

    const recipes = get(recipeStore);
    expect(recipes).toHaveLength(1);
    expect(recipes[0].title).toBe('テスト');
  });

  test('レシピを削除できる', () => {
    recipeStore.set([{ id: 1, title: 'テスト' }]);
    recipeStore.remove(1);

    const recipes = get(recipeStore);
    expect(recipes).toHaveLength(0);
  });
});
```

## 4. テストフィクスチャ

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from backend.api.main import app
from backend.api.deps import get_session
from backend.models.recipe import Recipe, RecipeIngredient, RecipeStep

@pytest.fixture(name="db_session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    def get_session_override():
        return db_session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_recipe(db_session):
    recipe = Recipe(
        title="サンプルレシピ",
        description="テスト用",
        servings=4
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    return recipe
```

## 5. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |
