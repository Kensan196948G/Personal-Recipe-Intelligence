"""
Export/Import Service for Recipe Intelligence

レシピデータのJSON形式でのエクスポート・インポート機能を提供
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError


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
        # TODO: DB実装後に実装
        # 仮実装
        return [
            RecipeExportSchema(
                id=1,
                title="サンプルレシピ",
                source_url="https://example.com/recipe/1",
                source_type="web",
                ingredients=[
                    {"name": "玉ねぎ", "amount": "1個", "unit": "個"},
                    {"name": "豚肉", "amount": "200", "unit": "g"},
                ],
                steps=["玉ねぎを切る", "豚肉を炒める", "調味料を加える"],
                cooking_time=30,
                servings=2,
                tags=["簡単", "時短"],
                notes="美味しいです",
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat(),
            )
        ]

    def _fetch_recipe_by_id(self, recipe_id: int) -> Optional[RecipeExportSchema]:
        """
        IDでレシピを取得

        Args:
            recipe_id: レシピID

        Returns:
            Optional[RecipeExportSchema]: レシピまたはNone
        """
        # TODO: DB実装後に実装
        # 仮実装
        if recipe_id == 1:
            return RecipeExportSchema(
                id=1,
                title="サンプルレシピ",
                source_url="https://example.com/recipe/1",
                source_type="web",
                ingredients=[
                    {"name": "玉ねぎ", "amount": "1個", "unit": "個"},
                ],
                steps=["玉ねぎを切る"],
                cooking_time=30,
                servings=2,
                tags=["簡単"],
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat(),
            )
        return None

    def _fetch_recipes_by_ids(self, recipe_ids: List[int]) -> List[RecipeExportSchema]:
        """
        複数IDでレシピを取得

        Args:
            recipe_ids: レシピIDのリスト

        Returns:
            List[RecipeExportSchema]: レシピリスト
        """
        # TODO: DB実装後に実装
        # 仮実装
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
        # TODO: DB実装後に実装
        # タイトルとURLで重複チェック
        # 仮実装として常にNoneを返す
        return None

    def _save_recipe(self, recipe_data: Dict[str, Any]) -> int:
        """
        レシピをDBに保存

        Args:
            recipe_data: レシピデータ

        Returns:
            int: 保存されたレシピのID
        """
        # TODO: DB実装後に実装
        # 仮実装
        return 999

    def _update_recipe(self, recipe_id: int, recipe_data: Dict[str, Any]) -> None:
        """
        既存レシピを更新

        Args:
            recipe_id: レシピID
            recipe_data: 新しいレシピデータ
        """
        # TODO: DB実装後に実装
        pass


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
