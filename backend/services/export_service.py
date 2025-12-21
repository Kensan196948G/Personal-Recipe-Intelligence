"""
Export/Import Service for Recipe Intelligence

レシピデータのJSON形式でのエクスポート・インポート機能を提供
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session
from backend.models import Recipe, Ingredient, Step, Tag
from backend.core.database import get_session


class RecipeExportSchema(BaseModel):
    """
    単一レシピのエクスポートスキーマ
    """

    id: Optional[int] = None
    title: str
    source_url: Optional[str] = None
    source_type: str = Field(default="manual")
    ingredients: List[Dict[str, Any]]
    steps: List[str]
    cooking_time: Optional[int] = None
    servings: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    image_path: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class RecipeExportContainer(BaseModel):
    """
    エクスポートデータのコンテナスキーマ
    """

    version: str = Field(default="1.0")
    exported_at: str
    recipe_count: int
    recipes: List[RecipeExportSchema]


class ImportValidationResult(BaseModel):
    """
    インポートバリデーション結果
    """

    is_valid: bool
    total_recipes: int
    valid_recipes: int
    invalid_recipes: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
    duplicates: List[Dict[str, Any]] = Field(default_factory=list)


class ImportResult(BaseModel):
    """
    インポート実行結果
    """

    success: bool
    imported_count: int
    skipped_count: int
    failed_count: int
    details: List[Dict[str, Any]] = Field(default_factory=list)


class ExportService:
    """
    レシピエクスポート/インポートサービス
    """

    def __init__(self, db_session):
        """
        Args:
            db_session: データベースセッション
        """
        self.db = db_session

    def export_all_recipes(self) -> Dict[str, Any]:
        """
        全レシピをJSON形式でエクスポート

        Returns:
            Dict[str, Any]: エクスポートデータ
        """
        # TODO: DB実装後に実装
        # 仮実装としてサンプルデータを返す
        recipes = self._fetch_all_recipes()

        export_data = RecipeExportContainer(
            version="1.0",
            exported_at=datetime.utcnow().isoformat(),
            recipe_count=len(recipes),
            recipes=recipes,
        )

        return export_data.model_dump()

    def export_single_recipe(self, recipe_id: int) -> Dict[str, Any]:
        """
        単一レシピをJSON形式でエクスポート

        Args:
            recipe_id: レシピID

        Returns:
            Dict[str, Any]: エクスポートデータ

        Raises:
            ValueError: レシピが見つからない場合
        """
        recipe = self._fetch_recipe_by_id(recipe_id)

        if not recipe:
            raise ValueError(f"Recipe with ID {recipe_id} not found")

        export_data = RecipeExportContainer(
            version="1.0",
            exported_at=datetime.utcnow().isoformat(),
            recipe_count=1,
            recipes=[recipe],
        )

        return export_data.model_dump()

    def export_batch_recipes(self, recipe_ids: List[int]) -> Dict[str, Any]:
        """
        選択したレシピ群をJSON形式でエクスポート

        Args:
            recipe_ids: レシピIDのリスト

        Returns:
            Dict[str, Any]: エクスポートデータ
        """
        recipes = self._fetch_recipes_by_ids(recipe_ids)

        export_data = RecipeExportContainer(
            version="1.0",
            exported_at=datetime.utcnow().isoformat(),
            recipe_count=len(recipes),
            recipes=recipes,
        )

        return export_data.model_dump()

    def validate_import_data(
        self, json_data: Dict[str, Any], check_duplicates: bool = True
    ) -> ImportValidationResult:
        """
        インポートデータのバリデーション

        Args:
            json_data: インポートするJSONデータ
            check_duplicates: 重複チェックを実行するか

        Returns:
            ImportValidationResult: バリデーション結果
        """
        errors = []
        warnings = []
        duplicates = []
        valid_count = 0
        invalid_count = 0

        # バージョンチェック
        version = json_data.get("version")
        if not version:
            warnings.append(
                {
                    "type": "missing_version",
                    "message": "Version field is missing, assuming 1.0",
                }
            )
        elif version != "1.0":
            warnings.append(
                {
                    "type": "version_mismatch",
                    "message": f"Version {version} may not be fully compatible",
                }
            )

        # レシピデータの検証
        recipes = json_data.get("recipes", [])
        if not recipes:
            errors.append(
                {"type": "no_recipes", "message": "No recipes found in import data"}
            )

        for idx, recipe_data in enumerate(recipes):
            try:
                # Pydanticモデルでバリデーション
                RecipeExportSchema(**recipe_data)
                valid_count += 1

                # 重複チェック
                if check_duplicates:
                    duplicate_info = self._check_duplicate(recipe_data)
                    if duplicate_info:
                        duplicates.append(
                            {
                                "index": idx,
                                "title": recipe_data.get("title"),
                                "duplicate_info": duplicate_info,
                            }
                        )

            except ValidationError as e:
                invalid_count += 1
                errors.append(
                    {
                        "index": idx,
                        "title": recipe_data.get("title", "Unknown"),
                        "type": "validation_error",
                        "details": e.errors(),
                    }
                )
            except Exception as e:
                invalid_count += 1
                errors.append(
                    {
                        "index": idx,
                        "title": recipe_data.get("title", "Unknown"),
                        "type": "unexpected_error",
                        "message": str(e),
                    }
                )

        is_valid = len(errors) == 0 and valid_count > 0

        return ImportValidationResult(
            is_valid=is_valid,
            total_recipes=len(recipes),
            valid_recipes=valid_count,
            invalid_recipes=invalid_count,
            errors=errors,
            warnings=warnings,
            duplicates=duplicates,
        )

    def import_recipes(
        self,
        json_data: Dict[str, Any],
        skip_duplicates: bool = True,
        overwrite_duplicates: bool = False,
    ) -> ImportResult:
        """
        JSONデータからレシピをインポート

        Args:
            json_data: インポートするJSONデータ
            skip_duplicates: 重複レシピをスキップするか
            overwrite_duplicates: 重複レシピを上書きするか

        Returns:
            ImportResult: インポート結果
        """
        # バリデーション実行
        validation_result = self.validate_import_data(json_data, check_duplicates=True)

        if not validation_result.is_valid:
            return ImportResult(
                success=False,
                imported_count=0,
                skipped_count=0,
                failed_count=validation_result.invalid_recipes,
                details=[
                    {
                        "type": "validation_failed",
                        "message": "Import validation failed",
                        "errors": validation_result.errors,
                    }
                ],
            )

        imported_count = 0
        skipped_count = 0
        failed_count = 0
        details = []

        recipes = json_data.get("recipes", [])

        for idx, recipe_data in enumerate(recipes):
            try:
                # 重複チェック
                duplicate_info = self._check_duplicate(recipe_data)

                if duplicate_info:
                    if skip_duplicates and not overwrite_duplicates:
                        skipped_count += 1
                        details.append(
                            {
                                "index": idx,
                                "title": recipe_data.get("title"),
                                "status": "skipped",
                                "reason": "duplicate",
                                "duplicate_id": duplicate_info.get("id"),
                            }
                        )
                        continue
                    elif overwrite_duplicates:
                        # 既存レシピを更新
                        self._update_recipe(duplicate_info.get("id"), recipe_data)
                        imported_count += 1
                        details.append(
                            {
                                "index": idx,
                                "title": recipe_data.get("title"),
                                "status": "updated",
                                "recipe_id": duplicate_info.get("id"),
                            }
                        )
                        continue

                # 新規レシピとして保存
                recipe_id = self._save_recipe(recipe_data)
                imported_count += 1
                details.append(
                    {
                        "index": idx,
                        "title": recipe_data.get("title"),
                        "status": "imported",
                        "recipe_id": recipe_id,
                    }
                )

            except Exception as e:
                failed_count += 1
                details.append(
                    {
                        "index": idx,
                        "title": recipe_data.get("title", "Unknown"),
                        "status": "failed",
                        "error": str(e),
                    }
                )

        return ImportResult(
            success=imported_count > 0,
            imported_count=imported_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
            details=details,
        )

    # ========================================
    # プライベートメソッド（DB操作）
    # ========================================

    def _fetch_all_recipes(self) -> List[RecipeExportSchema]:
        """
        全レシピをDBから取得

        Returns:
            List[RecipeExportSchema]: レシピリスト
        """
        recipes_list = []

        try:
            # Get all recipes from database
            all_recipes = self.db.query(Recipe).all()

            for recipe in all_recipes:
                # Convert ingredients
                ingredients_data = [
                    {
                        "name": ing.name,
                        "amount": str(ing.quantity) if ing.quantity else "",
                        "unit": ing.unit or "",
                    }
                    for ing in recipe.ingredients
                ] if recipe.ingredients else []

                # Convert steps
                steps_data = [
                    step.instruction
                    for step in sorted(recipe.steps, key=lambda s: s.step_number)
                ] if recipe.steps else []

                # Convert tags
                tags_data = [tag.name for tag in recipe.tags] if recipe.tags else []

                recipe_export = RecipeExportSchema(
                    id=recipe.id,
                    title=recipe.title,
                    source_url=recipe.source_url,
                    source_type=recipe.source_type,
                    ingredients=ingredients_data,
                    steps=steps_data,
                    cooking_time=recipe.total_time_minutes,
                    servings=recipe.servings,
                    tags=tags_data,
                    notes=recipe.notes,
                    image_path=recipe.image_path,
                    created_at=recipe.created_at.isoformat() if recipe.created_at else None,
                    updated_at=recipe.updated_at.isoformat() if recipe.updated_at else None,
                )
                recipes_list.append(recipe_export)

        except Exception as e:
            # If DB query fails, return empty list
            print(f"Error fetching recipes: {e}")

        return recipes_list

    def _fetch_recipe_by_id(self, recipe_id: int) -> Optional[RecipeExportSchema]:
        """
        IDでレシピを取得

        Args:
            recipe_id: レシピID

        Returns:
            Optional[RecipeExportSchema]: レシピまたはNone
        """
        try:
            recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()

            if not recipe:
                return None

            # Convert ingredients
            ingredients_data = [
                {
                    "name": ing.name,
                    "amount": str(ing.quantity) if ing.quantity else "",
                    "unit": ing.unit or "",
                }
                for ing in recipe.ingredients
            ] if recipe.ingredients else []

            # Convert steps
            steps_data = [
                step.instruction
                for step in sorted(recipe.steps, key=lambda s: s.step_number)
            ] if recipe.steps else []

            # Convert tags
            tags_data = [tag.name for tag in recipe.tags] if recipe.tags else []

            return RecipeExportSchema(
                id=recipe.id,
                title=recipe.title,
                source_url=recipe.source_url,
                source_type=recipe.source_type,
                ingredients=ingredients_data,
                steps=steps_data,
                cooking_time=recipe.total_time_minutes,
                servings=recipe.servings,
                tags=tags_data,
                notes=recipe.notes,
                image_path=recipe.image_path,
                created_at=recipe.created_at.isoformat() if recipe.created_at else None,
                updated_at=recipe.updated_at.isoformat() if recipe.updated_at else None,
            )

        except Exception as e:
            print(f"Error fetching recipe {recipe_id}: {e}")
            return None

    def _fetch_recipes_by_ids(self, recipe_ids: List[int]) -> List[RecipeExportSchema]:
        """
        複数IDでレシピを取得

        Args:
            recipe_ids: レシピIDのリスト

        Returns:
            List[RecipeExportSchema]: レシピリスト
        """
        recipes = []
        for recipe_id in recipe_ids:
            recipe = self._fetch_recipe_by_id(recipe_id)
            if recipe:
                recipes.append(recipe)
        return recipes

    def _check_duplicate(self, recipe_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        重複レシピをチェック

        Args:
            recipe_data: レシピデータ

        Returns:
            Optional[Dict[str, Any]]: 重複情報またはNone
        """
        try:
            title = recipe_data.get("title")
            source_url = recipe_data.get("source_url")

            # Check by title (exact match)
            if title:
                duplicate = self.db.query(Recipe).filter(Recipe.title == title).first()
                if duplicate:
                    return {
                        "id": duplicate.id,
                        "title": duplicate.title,
                        "match_type": "title"
                    }

            # Check by source URL (if provided)
            if source_url:
                duplicate = self.db.query(Recipe).filter(Recipe.source_url == source_url).first()
                if duplicate:
                    return {
                        "id": duplicate.id,
                        "title": duplicate.title,
                        "match_type": "url"
                    }

            return None

        except Exception as e:
            print(f"Error checking duplicate: {e}")
            return None

    def _save_recipe(self, recipe_data: Dict[str, Any]) -> int:
        """
        レシピをDBに保存

        Args:
            recipe_data: レシピデータ

        Returns:
            int: 保存されたレシピのID
        """
        try:
            # Create new recipe
            new_recipe = Recipe(
                title=recipe_data.get("title", ""),
                description=recipe_data.get("description"),
                source_url=recipe_data.get("source_url"),
                source_type=recipe_data.get("source_type", "manual"),
                servings=recipe_data.get("servings"),
                total_time_minutes=recipe_data.get("cooking_time"),
                notes=recipe_data.get("notes"),
                image_path=recipe_data.get("image_path"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(new_recipe)
            self.db.flush()  # Get ID without committing

            # Add ingredients
            if "ingredients" in recipe_data:
                for idx, ing_data in enumerate(recipe_data["ingredients"]):
                    ingredient = Ingredient(
                        recipe_id=new_recipe.id,
                        name=ing_data.get("name", ""),
                        name_normalized=ing_data.get("name", "").lower(),
                        quantity=float(ing_data.get("amount", "0")) if ing_data.get("amount") else None,
                        unit=ing_data.get("unit"),
                        order_index=idx
                    )
                    self.db.add(ingredient)

            # Add steps
            if "steps" in recipe_data:
                for step_num, step_text in enumerate(recipe_data["steps"], start=1):
                    step = Step(
                        recipe_id=new_recipe.id,
                        step_number=step_num,
                        instruction=step_text if isinstance(step_text, str) else str(step_text)
                    )
                    self.db.add(step)

            # Add tags
            if "tags" in recipe_data:
                for tag_name in recipe_data["tags"]:
                    # Find or create tag
                    tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name, created_at=datetime.utcnow())
                        self.db.add(tag)
                    new_recipe.tags.append(tag)

            self.db.commit()
            return new_recipe.id

        except Exception as e:
            self.db.rollback()
            print(f"Error saving recipe: {e}")
            raise

    def _update_recipe(self, recipe_id: int, recipe_data: Dict[str, Any]) -> None:
        """
        既存レシピを更新

        Args:
            recipe_id: レシピID
            recipe_data: 新しいレシピデータ
        """
        try:
            recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()

            if not recipe:
                raise ValueError(f"Recipe {recipe_id} not found")

            # Update basic fields
            recipe.title = recipe_data.get("title", recipe.title)
            recipe.description = recipe_data.get("description", recipe.description)
            recipe.source_url = recipe_data.get("source_url", recipe.source_url)
            recipe.servings = recipe_data.get("servings", recipe.servings)
            recipe.total_time_minutes = recipe_data.get("cooking_time", recipe.total_time_minutes)
            recipe.notes = recipe_data.get("notes", recipe.notes)
            recipe.updated_at = datetime.utcnow()

            # Delete existing ingredients and steps
            self.db.query(Ingredient).filter(Ingredient.recipe_id == recipe_id).delete()
            self.db.query(Step).filter(Step.recipe_id == recipe_id).delete()

            # Add new ingredients
            if "ingredients" in recipe_data:
                for idx, ing_data in enumerate(recipe_data["ingredients"]):
                    ingredient = Ingredient(
                        recipe_id=recipe.id,
                        name=ing_data.get("name", ""),
                        name_normalized=ing_data.get("name", "").lower(),
                        quantity=float(ing_data.get("amount", "0")) if ing_data.get("amount") else None,
                        unit=ing_data.get("unit"),
                        order_index=idx
                    )
                    self.db.add(ingredient)

            # Add new steps
            if "steps" in recipe_data:
                for step_num, step_text in enumerate(recipe_data["steps"], start=1):
                    step = Step(
                        recipe_id=recipe.id,
                        step_number=step_num,
                        instruction=step_text if isinstance(step_text, str) else str(step_text)
                    )
                    self.db.add(step)

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            print(f"Error updating recipe {recipe_id}: {e}")
            raise


def export_to_file(
    export_data: Dict[str, Any], file_path: str, indent: int = 2
) -> None:
    """
    エクスポートデータをファイルに保存

    Args:
        export_data: エクスポートデータ
        file_path: 保存先ファイルパス
        indent: JSONインデント幅
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=indent)


def import_from_file(file_path: str) -> Dict[str, Any]:
    """
    ファイルからインポートデータを読み込み

    Args:
        file_path: インポートファイルパス

    Returns:
        Dict[str, Any]: インポートデータ

    Raises:
        FileNotFoundError: ファイルが見つからない場合
        json.JSONDecodeError: JSON解析エラーの場合
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Import file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
