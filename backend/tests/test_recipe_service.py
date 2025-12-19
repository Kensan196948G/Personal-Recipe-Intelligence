"""
Recipe Service テスト

RecipeService のCRUD操作をテスト。
SQLModel Session を使用したフィクスチャを利用。
"""

import pytest
from backend.services.recipe_service import RecipeService
from backend.models.recipe import Recipe, Ingredient, Step, Tag


class TestRecipeService:
    """RecipeService のテスト"""

    def test_create_recipe(self, db_session):
        """レシピ作成のテスト"""
        service = RecipeService(db_session)

        recipe = service.create_recipe(
            title="カレーライス",
            description="簡単なカレー",
            cook_time_minutes=30,
        )

        assert recipe.id is not None
        assert recipe.title == "カレーライス"
        assert recipe.description == "簡単なカレー"
        assert recipe.created_at is not None

    def test_get_recipe(self, db_session):
        """レシピ取得のテスト"""
        service = RecipeService(db_session)

        # 作成
        created = service.create_recipe(title="テストレシピ")

        # 取得
        retrieved = service.get_recipe(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == "テストレシピ"

    def test_get_recipe_not_found(self, db_session):
        """存在しないレシピ取得"""
        service = RecipeService(db_session)
        recipe = service.get_recipe(99999)
        assert recipe is None

    def test_get_recipes_pagination(self, db_session):
        """レシピ一覧取得（ページネーション）のテスト"""
        service = RecipeService(db_session)

        # 5件作成
        for i in range(5):
            service.create_recipe(title=f"レシピ{i + 1}")

        # 1ページ目（3件）
        recipes, total = service.get_recipes(page=1, per_page=3)

        assert len(recipes) == 3
        assert total == 5
        assert recipes[0].title == "レシピ5"  # 新しい順

    def test_get_recipes_search(self, db_session):
        """レシピ検索のテスト"""
        service = RecipeService(db_session)

        service.create_recipe(title="カレーライス")
        service.create_recipe(title="チャーハン")
        service.create_recipe(title="カレーうどん")

        recipes, total = service.get_recipes(search="カレー")

        assert total == 2
        assert all("カレー" in r.title for r in recipes)

    def test_update_recipe(self, db_session):
        """レシピ更新のテスト"""
        service = RecipeService(db_session)

        created = service.create_recipe(
            title="元のタイトル",
            description="元の説明"
        )

        updated = service.update_recipe(
            created.id,
            title="新しいタイトル",
            description="新しい説明"
        )

        assert updated.title == "新しいタイトル"
        assert updated.description == "新しい説明"

    def test_update_recipe_not_found(self, db_session):
        """存在しないレシピの更新"""
        service = RecipeService(db_session)
        result = service.update_recipe(99999, title="新タイトル")
        assert result is None

    def test_delete_recipe(self, db_session):
        """レシピ削除のテスト"""
        service = RecipeService(db_session)

        created = service.create_recipe(title="削除対象")
        result = service.delete_recipe(created.id)

        assert result is True

        # 削除確認
        retrieved = service.get_recipe(created.id)
        assert retrieved is None

    def test_delete_recipe_not_found(self, db_session):
        """存在しないレシピの削除"""
        service = RecipeService(db_session)
        result = service.delete_recipe(99999)
        assert result is False


class TestRecipeServiceWithTags:
    """RecipeService タグ関連のテスト"""

    def test_create_recipe_with_tags(self, db_session):
        """タグ付きレシピ作成のテスト"""
        service = RecipeService(db_session)

        # タグを作成
        tag = Tag(name="和食")
        db_session.add(tag)
        db_session.commit()
        db_session.refresh(tag)

        # タグ付きレシピ作成
        recipe = service.create_recipe(
            title="和風カレー",
            tag_ids=[tag.id]
        )

        assert recipe.id is not None
        assert recipe.title == "和風カレー"

    def test_filter_recipes_by_tag(self, db_session):
        """タグでレシピをフィルタリング"""
        service = RecipeService(db_session)

        # タグを作成
        tag1 = Tag(name="和食")
        tag2 = Tag(name="洋食")
        db_session.add(tag1)
        db_session.add(tag2)
        db_session.commit()
        db_session.refresh(tag1)
        db_session.refresh(tag2)

        # レシピ作成
        service.create_recipe(title="和風カレー", tag_ids=[tag1.id])
        service.create_recipe(title="洋風カレー", tag_ids=[tag2.id])

        # タグでフィルタリング
        recipes, total = service.get_recipes(tag_id=tag1.id)

        assert total == 1
        assert recipes[0].title == "和風カレー"


class TestRecipeServiceStats:
    """RecipeService 統計関連のテスト"""

    def test_recipe_count(self, db_session):
        """レシピ総数のテスト"""
        service = RecipeService(db_session)

        # レシピ作成
        service.create_recipe(title="レシピ1", source_url="http://example.com")
        service.create_recipe(title="レシピ2")

        recipes, total = service.get_recipes()

        assert total == 2
