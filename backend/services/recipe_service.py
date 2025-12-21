"""
Recipe Service - Business logic for recipe operations

N+1クエリ問題を解決するために selectinload を使用
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

from backend.models.recipe import Ingredient, Recipe, RecipeTag, Step, Tag


class RecipeService:
    """レシピサービス"""

    def __init__(self, session: Session):
        self.session = session

    # ===========================================
    # Recipe CRUD
    # ===========================================
    def get_recipes(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        tag_id: Optional[int] = None,
    ) -> tuple[list[Recipe], int]:
        """レシピ一覧取得（N+1クエリ問題を解決）"""
        query = select(Recipe)

        # 検索フィルタ
        if search:
            query = query.where(Recipe.title.contains(search))

        # タグフィルタ
        if tag_id:
            query = query.join(RecipeTag).where(RecipeTag.tag_id == tag_id)

        # 総数取得
        count_query = select(func.count()).select_from(query.subquery())
        total = self.session.exec(count_query).one()

        # ページネーション + 関連データの事前読み込み（N+1クエリ問題を解決）
        offset = (page - 1) * per_page
        query = (
            query
            .options(
                selectinload(Recipe.ingredients),
                selectinload(Recipe.steps),
                selectinload(Recipe.tags),
            )
            .order_by(Recipe.id.desc())  # 新しい順に並べる（IDの降順で最新が先頭）
            .offset(offset)
            .limit(per_page)
        )

        recipes = self.session.exec(query).all()
        return list(recipes), total

    def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        """レシピ詳細取得（N+1クエリ問題を解決）"""
        query = (
            select(Recipe)
            .where(Recipe.id == recipe_id)
            .options(
                selectinload(Recipe.ingredients),
                selectinload(Recipe.steps),
                selectinload(Recipe.tags),
            )
        )
        return self.session.exec(query).first()

    def create_recipe(
        self,
        title: str,
        description: Optional[str] = None,
        servings: Optional[int] = None,
        prep_time_minutes: Optional[int] = None,
        cook_time_minutes: Optional[int] = None,
        source_url: Optional[str] = None,
        source_type: str = "manual",
        image_url: Optional[str] = None,
        ingredients: Optional[list[dict]] = None,
        steps: Optional[list[dict]] = None,
        tag_ids: Optional[list[int]] = None,
    ) -> Recipe:
        """レシピ作成"""
        recipe = Recipe(
            title=title,
            description=description,
            servings=servings,
            prep_time_minutes=prep_time_minutes,
            cook_time_minutes=cook_time_minutes,
            source_url=source_url,
            source_type=source_type,
            image_url=image_url,
        )
        self.session.add(recipe)
        self.session.flush()

        # 材料追加
        if ingredients:
            for idx, ing_data in enumerate(ingredients):
                name = ing_data["name"]
                name_normalized = ing_data.get("name_normalized") or name
                ingredient = Ingredient(
                    recipe_id=recipe.id,
                    name=name,
                    name_normalized=name_normalized,
                    amount=ing_data.get("amount"),
                    unit=ing_data.get("unit"),
                    note=ing_data.get("note"),
                    order=ing_data.get("order", idx),
                )
                self.session.add(ingredient)

        # 手順追加
        if steps:
            for step_data in steps:
                step = Step(
                    recipe_id=recipe.id,
                    description=step_data["description"],
                    order=step_data["order"],
                )
                self.session.add(step)

        # タグ追加
        if tag_ids:
            existing_tag_ids = set(
                self.session.exec(
                    select(Tag.id).where(Tag.id.in_(tag_ids))
                ).all()
            )
            for tag_id in tag_ids:
                if tag_id in existing_tag_ids:
                    recipe_tag = RecipeTag(recipe_id=recipe.id, tag_id=tag_id)
                    self.session.add(recipe_tag)

        self.session.commit()
        self.session.refresh(recipe)
        return recipe

    def update_recipe(
        self,
        recipe_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        servings: Optional[int] = None,
        prep_time_minutes: Optional[int] = None,
        cook_time_minutes: Optional[int] = None,
        source_url: Optional[str] = None,
        source_type: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> Optional[Recipe]:
        """レシピ更新"""
        recipe = self.session.get(Recipe, recipe_id)
        if not recipe:
            return None

        if title is not None:
            recipe.title = title
        if description is not None:
            recipe.description = description
        if servings is not None:
            recipe.servings = servings
        if prep_time_minutes is not None:
            recipe.prep_time_minutes = prep_time_minutes
        if cook_time_minutes is not None:
            recipe.cook_time_minutes = cook_time_minutes
        if source_url is not None:
            recipe.source_url = source_url
        if source_type is not None:
            recipe.source_type = source_type
        if image_url is not None:
            recipe.image_url = image_url

        recipe.updated_at = datetime.now()
        self.session.commit()
        self.session.refresh(recipe)
        return recipe

    def delete_recipe(self, recipe_id: int) -> bool:
        """レシピ削除"""
        recipe = self.session.get(Recipe, recipe_id)
        if not recipe:
            return False

        # 関連データ削除
        for ingredient in recipe.ingredients:
            self.session.delete(ingredient)
        for step in recipe.steps:
            self.session.delete(step)
        for recipe_tag in recipe.tags:
            self.session.delete(recipe_tag)

        self.session.delete(recipe)
        self.session.commit()
        return True

    # ===========================================
    # Ingredient Operations
    # ===========================================
    def add_ingredient(
        self, recipe_id: int, ingredient_data: dict
    ) -> Optional[Ingredient]:
        """材料追加"""
        recipe = self.session.get(Recipe, recipe_id)
        if not recipe:
            return None

        name = ingredient_data["name"]
        name_normalized = ingredient_data.get("name_normalized") or name
        ingredient = Ingredient(
            recipe_id=recipe_id,
            name=name,
            name_normalized=name_normalized,
            amount=ingredient_data.get("amount"),
            unit=ingredient_data.get("unit"),
            note=ingredient_data.get("note"),
            order=ingredient_data.get("order", len(recipe.ingredients)),
        )
        self.session.add(ingredient)
        self.session.commit()
        self.session.refresh(ingredient)
        return ingredient

    def update_ingredient(self, ingredient_id: int, data: dict) -> Optional[Ingredient]:
        """材料更新"""
        ingredient = self.session.get(Ingredient, ingredient_id)
        if not ingredient:
            return None

        for key, value in data.items():
            if value is not None and hasattr(ingredient, key):
                setattr(ingredient, key, value)

        self.session.commit()
        self.session.refresh(ingredient)
        return ingredient

    def delete_ingredient(self, ingredient_id: int) -> bool:
        """材料削除"""
        ingredient = self.session.get(Ingredient, ingredient_id)
        if not ingredient:
            return False

        self.session.delete(ingredient)
        self.session.commit()
        return True

    # ===========================================
    # Step Operations
    # ===========================================
    def add_step(self, recipe_id: int, step_data: dict) -> Optional[Step]:
        """手順追加"""
        recipe = self.session.get(Recipe, recipe_id)
        if not recipe:
            return None

        step = Step(
            recipe_id=recipe_id,
            description=step_data["description"],
            order=step_data["order"],
        )
        self.session.add(step)
        self.session.commit()
        self.session.refresh(step)
        return step

    def update_step(self, step_id: int, data: dict) -> Optional[Step]:
        """手順更新"""
        step = self.session.get(Step, step_id)
        if not step:
            return None

        for key, value in data.items():
            if value is not None and hasattr(step, key):
                setattr(step, key, value)

        self.session.commit()
        self.session.refresh(step)
        return step

    def delete_step(self, step_id: int) -> bool:
        """手順削除"""
        step = self.session.get(Step, step_id)
        if not step:
            return False

        self.session.delete(step)
        self.session.commit()
        return True

    # ===========================================
    # Dashboard Statistics
    # ===========================================
    def count_recipes_since(self, since: datetime) -> int:
        """指定日時以降に作成されたレシピ数を取得"""
        query = select(func.count()).select_from(Recipe).where(Recipe.created_at >= since)
        return self.session.exec(query).one() or 0

    def count_favorites(self) -> int:
        """お気に入りレシピ数を取得"""
        query = select(func.count()).select_from(Recipe).where(Recipe.is_favorite == True)
        return self.session.exec(query).one() or 0

    def count_tags(self) -> int:
        """タグ数を取得"""
        query = select(func.count()).select_from(Tag)
        return self.session.exec(query).one() or 0

    def get_source_type_stats(self) -> dict:
        """ソースタイプ別の統計を取得"""
        query = (
            select(Recipe.source_type, func.count(Recipe.id))
            .group_by(Recipe.source_type)
        )
        results = self.session.exec(query).all()
        return {source_type: count for source_type, count in results}


class TagService:
    """タグサービス"""

    def __init__(self, session: Session):
        self.session = session

    def get_tags(self) -> list[Tag]:
        """タグ一覧取得"""
        return list(self.session.exec(select(Tag).order_by(Tag.name)).all())

    def get_tag(self, tag_id: int) -> Optional[Tag]:
        """タグ取得"""
        return self.session.get(Tag, tag_id)

    def create_tag(self, name: str) -> Tag:
        """タグ作成"""
        tag = Tag(name=name)
        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)
        return tag

    def delete_tag(self, tag_id: int) -> bool:
        """タグ削除"""
        tag = self.session.get(Tag, tag_id)
        if not tag:
            return False

        # 関連レシピタグ削除
        recipe_tags = self.session.exec(
            select(RecipeTag).where(RecipeTag.tag_id == tag_id)
        ).all()
        for rt in recipe_tags:
            self.session.delete(rt)

        self.session.delete(tag)
        self.session.commit()
        return True
