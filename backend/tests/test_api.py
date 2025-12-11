"""
API Tests - Full CRUD operations test suite
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from backend.api.main import app
from backend.core.database import get_session


# テスト用データベース設定
@pytest.fixture(name="session")
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
def client_fixture(session: Session):
  def get_session_override():
    return session

  app.dependency_overrides[get_session] = get_session_override
  client = TestClient(app)
  yield client
  app.dependency_overrides.clear()


# ===========================================
# Basic Endpoint Tests
# ===========================================
def test_root(client: TestClient):
  """ルートエンドポイントのテスト"""
  response = client.get("/")
  assert response.status_code == 200
  data = response.json()
  assert data["status"] == "ok"


def test_health_check(client: TestClient):
  """ヘルスチェックのテスト"""
  response = client.get("/health")
  assert response.status_code == 200
  data = response.json()
  assert data["status"] == "ok"
  assert data["data"]["service"] == "healthy"


# ===========================================
# Recipe CRUD Tests
# ===========================================
def test_get_recipes_empty(client: TestClient):
  """空のレシピ一覧取得テスト"""
  response = client.get("/api/v1/recipes")
  assert response.status_code == 200
  data = response.json()
  assert data["status"] == "ok"
  assert data["data"]["items"] == []
  assert data["data"]["total"] == 0


def test_create_recipe(client: TestClient):
  """レシピ作成テスト"""
  recipe_data = {
    "title": "テストレシピ",
    "description": "テスト用のレシピです",
    "servings": 2,
    "prep_time_minutes": 10,
    "cook_time_minutes": 20,
    "source_type": "manual",
    "ingredients": [
      {"name": "玉ねぎ", "amount": 1.0, "unit": "個", "order": 0},
      {"name": "にんにく", "amount": 2.0, "unit": "片", "order": 1},
    ],
    "steps": [
      {"description": "玉ねぎをみじん切りにする", "order": 1},
      {"description": "にんにくをみじん切りにする", "order": 2},
    ],
  }

  response = client.post("/api/v1/recipes", json=recipe_data)
  assert response.status_code == 201
  data = response.json()
  assert data["status"] == "ok"
  assert data["data"]["title"] == "テストレシピ"
  assert "id" in data["data"]


def test_get_recipe(client: TestClient):
  """レシピ詳細取得テスト"""
  # まずレシピを作成
  recipe_data = {"title": "取得テストレシピ", "source_type": "manual"}
  create_response = client.post("/api/v1/recipes", json=recipe_data)
  recipe_id = create_response.json()["data"]["id"]

  # 作成したレシピを取得
  response = client.get(f"/api/v1/recipes/{recipe_id}")
  assert response.status_code == 200
  data = response.json()
  assert data["status"] == "ok"
  assert data["data"]["id"] == recipe_id
  assert data["data"]["title"] == "取得テストレシピ"


def test_get_recipe_not_found(client: TestClient):
  """存在しないレシピ取得テスト"""
  response = client.get("/api/v1/recipes/99999")
  assert response.status_code == 404


def test_update_recipe(client: TestClient):
  """レシピ更新テスト"""
  # レシピ作成
  recipe_data = {"title": "更新前レシピ", "source_type": "manual"}
  create_response = client.post("/api/v1/recipes", json=recipe_data)
  recipe_id = create_response.json()["data"]["id"]

  # レシピ更新
  update_data = {"title": "更新後レシピ", "description": "更新されました"}
  response = client.put(f"/api/v1/recipes/{recipe_id}", json=update_data)
  assert response.status_code == 200
  data = response.json()
  assert data["data"]["title"] == "更新後レシピ"


def test_delete_recipe(client: TestClient):
  """レシピ削除テスト"""
  # レシピ作成
  recipe_data = {"title": "削除テストレシピ", "source_type": "manual"}
  create_response = client.post("/api/v1/recipes", json=recipe_data)
  recipe_id = create_response.json()["data"]["id"]

  # レシピ削除
  response = client.delete(f"/api/v1/recipes/{recipe_id}")
  assert response.status_code == 200
  assert response.json()["data"]["deleted"] is True

  # 削除確認
  get_response = client.get(f"/api/v1/recipes/{recipe_id}")
  assert get_response.status_code == 404


def test_get_recipes_with_pagination(client: TestClient):
  """ページネーション付きレシピ一覧取得テスト"""
  # 複数のレシピを作成
  for i in range(5):
    client.post(
      "/api/v1/recipes", json={"title": f"レシピ{i}", "source_type": "manual"}
    )

  # ページネーション確認
  response = client.get("/api/v1/recipes?page=1&per_page=2")
  assert response.status_code == 200
  data = response.json()
  assert len(data["data"]["items"]) == 2
  assert data["data"]["total"] == 5
  assert data["data"]["total_pages"] == 3


def test_get_recipes_with_search(client: TestClient):
  """検索付きレシピ一覧取得テスト"""
  # レシピ作成
  client.post(
    "/api/v1/recipes", json={"title": "カレーライス", "source_type": "manual"}
  )
  client.post(
    "/api/v1/recipes", json={"title": "ハンバーグ", "source_type": "manual"}
  )

  # 検索
  response = client.get("/api/v1/recipes?search=カレー")
  assert response.status_code == 200
  data = response.json()
  assert len(data["data"]["items"]) == 1
  assert data["data"]["items"][0]["title"] == "カレーライス"


# ===========================================
# Ingredient Tests
# ===========================================
def test_add_ingredient(client: TestClient):
  """材料追加テスト"""
  # レシピ作成
  create_response = client.post(
    "/api/v1/recipes", json={"title": "材料テスト", "source_type": "manual"}
  )
  recipe_id = create_response.json()["data"]["id"]

  # 材料追加
  ingredient_data = {"name": "人参", "amount": 2.0, "unit": "本", "order": 0}
  response = client.post(
    f"/api/v1/recipes/{recipe_id}/ingredients", json=ingredient_data
  )
  assert response.status_code == 201
  data = response.json()
  assert data["data"]["name"] == "人参"


def test_update_ingredient(client: TestClient):
  """材料更新テスト"""
  # レシピと材料作成
  create_response = client.post(
    "/api/v1/recipes",
    json={
      "title": "材料更新テスト",
      "source_type": "manual",
      "ingredients": [{"name": "更新前材料", "amount": 1.0, "unit": "個", "order": 0}],
    },
  )
  recipe_id = create_response.json()["data"]["id"]

  # レシピ詳細取得して材料ID取得
  detail_response = client.get(f"/api/v1/recipes/{recipe_id}")
  ingredient_id = detail_response.json()["data"]["ingredients"][0]["id"]

  # 材料更新
  update_data = {"name": "更新後材料", "amount": 3.0}
  response = client.put(
    f"/api/v1/recipes/{recipe_id}/ingredients/{ingredient_id}", json=update_data
  )
  assert response.status_code == 200
  assert response.json()["data"]["name"] == "更新後材料"


def test_delete_ingredient(client: TestClient):
  """材料削除テスト"""
  # レシピと材料作成
  create_response = client.post(
    "/api/v1/recipes",
    json={
      "title": "材料削除テスト",
      "source_type": "manual",
      "ingredients": [{"name": "削除材料", "amount": 1.0, "unit": "個", "order": 0}],
    },
  )
  recipe_id = create_response.json()["data"]["id"]

  # 材料ID取得
  detail_response = client.get(f"/api/v1/recipes/{recipe_id}")
  ingredient_id = detail_response.json()["data"]["ingredients"][0]["id"]

  # 材料削除
  response = client.delete(
    f"/api/v1/recipes/{recipe_id}/ingredients/{ingredient_id}"
  )
  assert response.status_code == 200
  assert response.json()["data"]["deleted"] is True


# ===========================================
# Step Tests
# ===========================================
def test_add_step(client: TestClient):
  """手順追加テスト"""
  # レシピ作成
  create_response = client.post(
    "/api/v1/recipes", json={"title": "手順テスト", "source_type": "manual"}
  )
  recipe_id = create_response.json()["data"]["id"]

  # 手順追加
  step_data = {"description": "フライパンを熱する", "order": 1}
  response = client.post(f"/api/v1/recipes/{recipe_id}/steps", json=step_data)
  assert response.status_code == 201
  data = response.json()
  assert data["data"]["description"] == "フライパンを熱する"


def test_update_step(client: TestClient):
  """手順更新テスト"""
  # レシピと手順作成
  create_response = client.post(
    "/api/v1/recipes",
    json={
      "title": "手順更新テスト",
      "source_type": "manual",
      "steps": [{"description": "更新前手順", "order": 1}],
    },
  )
  recipe_id = create_response.json()["data"]["id"]

  # 手順ID取得
  detail_response = client.get(f"/api/v1/recipes/{recipe_id}")
  step_id = detail_response.json()["data"]["steps"][0]["id"]

  # 手順更新
  update_data = {"description": "更新後手順"}
  response = client.put(
    f"/api/v1/recipes/{recipe_id}/steps/{step_id}", json=update_data
  )
  assert response.status_code == 200
  assert response.json()["data"]["description"] == "更新後手順"


def test_delete_step(client: TestClient):
  """手順削除テスト"""
  # レシピと手順作成
  create_response = client.post(
    "/api/v1/recipes",
    json={
      "title": "手順削除テスト",
      "source_type": "manual",
      "steps": [{"description": "削除手順", "order": 1}],
    },
  )
  recipe_id = create_response.json()["data"]["id"]

  # 手順ID取得
  detail_response = client.get(f"/api/v1/recipes/{recipe_id}")
  step_id = detail_response.json()["data"]["steps"][0]["id"]

  # 手順削除
  response = client.delete(f"/api/v1/recipes/{recipe_id}/steps/{step_id}")
  assert response.status_code == 200
  assert response.json()["data"]["deleted"] is True


# ===========================================
# Tag Tests
# ===========================================
def test_get_tags_empty(client: TestClient):
  """空のタグ一覧取得テスト"""
  response = client.get("/api/v1/tags")
  assert response.status_code == 200
  data = response.json()
  assert data["status"] == "ok"
  assert data["data"] == []


def test_create_tag(client: TestClient):
  """タグ作成テスト"""
  response = client.post("/api/v1/tags", json={"name": "和食"})
  assert response.status_code == 201
  data = response.json()
  assert data["data"]["name"] == "和食"


def test_get_tag(client: TestClient):
  """タグ取得テスト"""
  # タグ作成
  create_response = client.post("/api/v1/tags", json={"name": "洋食"})
  tag_id = create_response.json()["data"]["id"]

  # タグ取得
  response = client.get(f"/api/v1/tags/{tag_id}")
  assert response.status_code == 200
  assert response.json()["data"]["name"] == "洋食"


def test_delete_tag(client: TestClient):
  """タグ削除テスト"""
  # タグ作成
  create_response = client.post("/api/v1/tags", json={"name": "削除タグ"})
  tag_id = create_response.json()["data"]["id"]

  # タグ削除
  response = client.delete(f"/api/v1/tags/{tag_id}")
  assert response.status_code == 200
  assert response.json()["data"]["deleted"] is True

  # 削除確認
  get_response = client.get(f"/api/v1/tags/{tag_id}")
  assert get_response.status_code == 404
