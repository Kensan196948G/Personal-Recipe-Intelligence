"""
Recipe Service テスト
"""

import pytest
import os
import tempfile

from backend.repositories.recipe_repository import RecipeRepository
from backend.services.recipe_service import RecipeService


@pytest.fixture
def temp_db():
    """テスト用の一時 DB を作成"""
    fd, path = tempfile.mkstemp(suffix=".db")
    yield path
    os.close(fd)
    os.unlink(path)


@pytest.fixture
def repository(temp_db):
    """テスト用リポジトリ"""
    return RecipeRepository(db_path=temp_db)


@pytest.fixture
def service(repository):
    """テスト用サービス"""
    return RecipeService(repository=repository)


class TestRecipeService:
    """RecipeService のテスト"""

    def test_create_recipe(self, service):
        """レシピ作成のテスト"""
        recipe_data = {
            "title": "カレーライス",
            "description": "簡単なカレー",
            "ingredients": ["じゃがいも", "にんじん", "たまねぎ"],
            "steps": ["材料を切る", "煮込む", "ルーを入れる"],
            "tags": ["和食", "簡単"],
        }

        recipe = service.create_recipe(recipe_data)

        assert recipe.id is not None
        assert recipe.title == "カレーライス"
        assert len(recipe.ingredients) == 3
        assert recipe.created_at is not None

    def test_create_recipe_without_title(self, service):
        """タイトルなしでレシピ作成（エラー）"""
        recipe_data = {"description": "説明のみ"}

        with pytest.raises(ValueError, match="タイトルは必須です"):
            service.create_recipe(recipe_data)

    def test_get_recipe(self, service):
        """レシピ取得のテスト"""
        recipe_data = {"title": "テストレシピ"}
        created = service.create_recipe(recipe_data)

        retrieved = service.get_recipe(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == "テストレシピ"

    def test_get_recipe_not_found(self, service):
        """存在しないレシピ取得"""
        recipe = service.get_recipe(99999)
        assert recipe is None

    def test_get_all_recipes(self, service):
        """全レシピ取得のテスト"""
        # 3件作成
        for i in range(3):
            service.create_recipe({"title": f"レシピ{i+1}"})

        recipes = service.get_all_recipes()

        assert len(recipes) == 3
        assert recipes[0].title == "レシピ3"  # 新しい順

    def test_update_recipe(self, service):
        """レシピ更新のテスト"""
        recipe_data = {"title": "元のタイトル", "description": "元の説明"}
        created = service.create_recipe(recipe_data)

        update_data = {"title": "新しいタイトル", "description": "新しい説明"}
        updated = service.update_recipe(created.id, update_data)

        assert updated.title == "新しいタイトル"
        assert updated.description == "新しい説明"

    def test_update_recipe_not_found(self, service):
        """存在しないレシピの更新"""
        result = service.update_recipe(99999, {"title": "新タイトル"})
        assert result is None

    def test_delete_recipe(self, service):
        """レシピ削除のテスト"""
        recipe_data = {"title": "削除対象"}
        created = service.create_recipe(recipe_data)

        result = service.delete_recipe(created.id)
        assert result is True

        # 削除確認
        retrieved = service.get_recipe(created.id)
        assert retrieved is None

    def test_delete_recipe_not_found(self, service):
        """存在しないレシピの削除"""
        result = service.delete_recipe(99999)
        assert result is False

    def test_search_recipes_by_keyword(self, service):
        """キーワード検索のテスト"""
        service.create_recipe({"title": "カレーライス"})
        service.create_recipe({"title": "チャーハン"})
        service.create_recipe({"title": "カレーうどん"})

        results = service.search_recipes(keyword="カレー")

        assert len(results) == 2
        assert all("カレー" in r.title for r in results)

    def test_search_recipes_by_tags(self, service):
        """タグ検索のテスト"""
        service.create_recipe({"title": "レシピ1", "tags": ["和食", "簡単"]})
        service.create_recipe({"title": "レシピ2", "tags": ["洋食"]})
        service.create_recipe({"title": "レシピ3", "tags": ["和食", "本格"]})

        results = service.search_recipes(tags=["和食"])

        assert len(results) == 2

    def test_get_recipes_by_tag(self, service):
        """タグでレシピ取得"""
        service.create_recipe({"title": "レシピA", "tags": ["簡単"]})
        service.create_recipe({"title": "レシピB", "tags": ["本格"]})

        results = service.get_recipes_by_tag("簡単")

        assert len(results) == 1
        assert results[0].title == "レシピA"

    def test_get_all_tags(self, service):
        """全タグ取得のテスト"""
        service.create_recipe({"title": "レシピ1", "tags": ["和食", "簡単"]})
        service.create_recipe({"title": "レシピ2", "tags": ["洋食", "簡単"]})

        tags = service.get_all_tags()

        assert len(tags) == 3
        assert "和食" in tags
        assert "洋食" in tags
        assert "簡単" in tags

    def test_get_recipe_count(self, service):
        """レシピ総数取得のテスト"""
        for i in range(5):
            service.create_recipe({"title": f"レシピ{i+1}"})

        count = service.get_recipe_count()
        assert count == 5

    def test_get_statistics(self, service):
        """統計情報取得のテスト"""
        service.create_recipe(
            {"title": "レシピ1", "tags": ["和食"], "source_url": "http://example.com"}
        )
        service.create_recipe(
            {"title": "レシピ2", "tags": ["洋食"], "image_path": "/path/to/image.jpg"}
        )

        stats = service.get_statistics()

        assert stats["total_recipes"] == 2
        assert stats["total_tags"] == 2
        assert stats["recipes_with_images"] == 1
        assert stats["recipes_with_source"] == 1

    def test_bulk_create_recipes(self, service):
        """一括作成のテスト"""
        recipes_data = [{"title": f"レシピ{i+1}"} for i in range(3)]

        created = service.bulk_create_recipes(recipes_data)

        assert len(created) == 3

    def test_bulk_delete_recipes(self, service):
        """一括削除のテスト"""
        ids = []
        for i in range(3):
            recipe = service.create_recipe({"title": f"レシピ{i+1}"})
            ids.append(recipe.id)

        deleted_count = service.bulk_delete_recipes(ids)

        assert deleted_count == 3
        assert service.get_recipe_count() == 0

    def test_export_recipe_to_json(self, service):
        """JSON エクスポートのテスト"""
        recipe_data = {
            "title": "エクスポートテスト",
            "ingredients": ["材料1", "材料2"],
            "steps": ["手順1"],
        }
        created = service.create_recipe(recipe_data)

        json_str = service.export_recipe_to_json(created.id)

        assert json_str is not None
        assert "エクスポートテスト" in json_str
        assert "材料1" in json_str

    def test_import_recipe_from_json(self, service):
        """JSON インポートのテスト"""
        json_str = """
    {
      "title": "インポートテスト",
      "description": "テスト説明",
      "ingredients": ["材料A"],
      "steps": ["手順A"],
      "tags": ["test"]
    }
    """

        recipe = service.import_recipe_from_json(json_str)

        assert recipe.id is not None
        assert recipe.title == "インポートテスト"
        assert len(recipe.ingredients) == 1

    def test_import_recipe_invalid_json(self, service):
        """不正な JSON のインポート"""
        with pytest.raises(ValueError, match="無効な JSON 形式です"):
            service.import_recipe_from_json("{ invalid json")
