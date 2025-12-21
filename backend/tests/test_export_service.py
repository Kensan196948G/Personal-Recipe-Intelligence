"""
Export Service Unit Tests

エクスポート/インポートサービスのテスト
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from backend.services.export_service import (
    ExportService,
    RecipeExportSchema,
    RecipeExportContainer,
    ImportValidationResult,
    ImportResult,
    export_to_file,
    import_from_file,
)


# ========================================
# Fixtures
# ========================================


@pytest.fixture
def export_service():
    """
    ExportServiceのフィクスチャ
    """
    return ExportService(db_session=None)


@pytest.fixture
def sample_recipe_data() -> Dict[str, Any]:
    """
    サンプルレシピデータ
    """
    return {
        "id": 1,
        "title": "テストレシピ",
        "source_url": "https://example.com/recipe/1",
        "source_type": "web",
        "ingredients": [
            {"name": "玉ねぎ", "amount": "1", "unit": "個"},
            {"name": "豚肉", "amount": "200", "unit": "g"},
        ],
        "steps": ["玉ねぎを切る", "豚肉を炒める", "調味料を加える"],
        "cooking_time": 30,
        "servings": 2,
        "tags": ["簡単", "時短"],
        "notes": "美味しいです",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_export_data(sample_recipe_data) -> Dict[str, Any]:
    """
    サンプルエクスポートデータ
    """
    return {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "recipe_count": 1,
        "recipes": [sample_recipe_data],
    }


# ========================================
# Schema Tests
# ========================================


def test_recipe_export_schema_valid(sample_recipe_data):
    """
    RecipeExportSchemaの正常バリデーション
    """
    recipe = RecipeExportSchema(**sample_recipe_data)

    assert recipe.title == "テストレシピ"
    assert recipe.cooking_time == 30
    assert len(recipe.ingredients) == 2
    assert len(recipe.steps) == 3
    assert len(recipe.tags) == 2


def test_recipe_export_schema_minimal():
    """
    最小限のデータでのバリデーション
    """
    minimal_data = {
        "title": "最小レシピ",
        "ingredients": [],
        "steps": ["手順1"],
    }

    recipe = RecipeExportSchema(**minimal_data)

    assert recipe.title == "最小レシピ"
    assert recipe.source_type == "manual"
    assert len(recipe.tags) == 0


def test_recipe_export_container_schema(sample_export_data):
    """
    RecipeExportContainerのバリデーション
    """
    container = RecipeExportContainer(**sample_export_data)

    assert container.version == "1.0"
    assert container.recipe_count == 1
    assert len(container.recipes) == 1
    assert container.recipes[0].title == "テストレシピ"


# ========================================
# Export Tests
# ========================================


def test_export_all_recipes(export_service):
    """
    全レシピエクスポートのテスト
    """
    result = export_service.export_all_recipes()

    assert "version" in result
    assert "exported_at" in result
    assert "recipe_count" in result
    assert "recipes" in result
    assert result["version"] == "1.0"
    assert isinstance(result["recipes"], list)


def test_export_single_recipe(export_service):
    """
    単一レシピエクスポートのテスト
    """
    result = export_service.export_single_recipe(1)

    assert result["version"] == "1.0"
    assert result["recipe_count"] == 1
    assert len(result["recipes"]) == 1
    assert result["recipes"][0]["title"] == "サンプルレシピ"


def test_export_single_recipe_not_found(export_service):
    """
    存在しないレシピのエクスポート
    """
    with pytest.raises(ValueError, match="Recipe with ID 999 not found"):
        export_service.export_single_recipe(999)


def test_export_batch_recipes(export_service):
    """
    バッチエクスポートのテスト
    """
    recipe_ids = [1]
    result = export_service.export_batch_recipes(recipe_ids)

    assert result["version"] == "1.0"
    assert result["recipe_count"] == 1
    assert len(result["recipes"]) == 1


def test_export_batch_recipes_empty(export_service):
    """
    空のIDリストでのバッチエクスポート
    """
    result = export_service.export_batch_recipes([])

    assert result["recipe_count"] == 0
    assert len(result["recipes"]) == 0


# ========================================
# Validation Tests
# ========================================


def test_validate_import_data_valid(export_service, sample_export_data):
    """
    正常なインポートデータのバリデーション
    """
    result = export_service.validate_import_data(
        sample_export_data, check_duplicates=False
    )

    assert result.is_valid is True
    assert result.total_recipes == 1
    assert result.valid_recipes == 1
    assert result.invalid_recipes == 0
    assert len(result.errors) == 0


def test_validate_import_data_missing_version(export_service, sample_export_data):
    """
    バージョン情報がないデータのバリデーション
    """
    data_without_version = sample_export_data.copy()
    del data_without_version["version"]

    result = export_service.validate_import_data(
        data_without_version, check_duplicates=False
    )

    assert result.is_valid is True
    assert len(result.warnings) >= 1
    assert any(w["type"] == "missing_version" for w in result.warnings)


def test_validate_import_data_wrong_version(export_service, sample_export_data):
    """
    異なるバージョンのデータのバリデーション
    """
    sample_export_data["version"] = "2.0"

    result = export_service.validate_import_data(
        sample_export_data, check_duplicates=False
    )

    assert result.is_valid is True
    assert len(result.warnings) >= 1
    assert any(w["type"] == "version_mismatch" for w in result.warnings)


def test_validate_import_data_no_recipes(export_service):
    """
    レシピがないデータのバリデーション
    """
    empty_data = {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "recipe_count": 0,
        "recipes": [],
    }

    result = export_service.validate_import_data(empty_data, check_duplicates=False)

    assert result.is_valid is False
    assert len(result.errors) >= 1
    assert any(e["type"] == "no_recipes" for e in result.errors)


def test_validate_import_data_invalid_recipe(export_service):
    """
    不正なレシピデータのバリデーション
    """
    invalid_data = {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "recipe_count": 1,
        "recipes": [
            {
                # titleが欠けている
                "ingredients": [],
                "steps": [],
            }
        ],
    }

    result = export_service.validate_import_data(invalid_data, check_duplicates=False)

    assert result.is_valid is False
    assert result.invalid_recipes == 1
    assert len(result.errors) >= 1
    assert result.errors[0]["type"] == "validation_error"


# ========================================
# Import Tests
# ========================================


def test_import_recipes_success(export_service, sample_export_data):
    """
    正常なレシピインポート
    """
    result = export_service.import_recipes(
        sample_export_data, skip_duplicates=True, overwrite_duplicates=False
    )

    assert result.success is True
    assert result.imported_count == 1
    assert result.skipped_count == 0
    assert result.failed_count == 0


def test_import_recipes_validation_failed(export_service):
    """
    バリデーション失敗時のインポート
    """
    invalid_data = {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "recipe_count": 1,
        "recipes": [{"ingredients": [], "steps": []}],  # titleが欠けている
    }

    result = export_service.import_recipes(
        invalid_data, skip_duplicates=True, overwrite_duplicates=False
    )

    assert result.success is False
    assert result.imported_count == 0


# ========================================
# File I/O Tests
# ========================================


def test_export_to_file(tmp_path, sample_export_data):
    """
    ファイルへのエクスポート
    """
    file_path = tmp_path / "test_export.json"

    export_to_file(sample_export_data, str(file_path))

    assert file_path.exists()


def test_import_from_file(tmp_path, sample_export_data):
    """
    ファイルからのインポート
    """
    file_path = tmp_path / "test_import.json"

    # まずエクスポート
    export_to_file(sample_export_data, str(file_path))

    # インポート
    imported_data = import_from_file(str(file_path))

    assert imported_data["version"] == sample_export_data["version"]
    assert imported_data["recipe_count"] == sample_export_data["recipe_count"]


def test_import_from_file_not_found():
    """
    存在しないファイルからのインポート
    """
    with pytest.raises(FileNotFoundError):
        import_from_file("/nonexistent/path/file.json")


# ========================================
# Edge Cases
# ========================================


def test_export_batch_with_invalid_ids(export_service):
    """
    存在しないIDを含むバッチエクスポート
    """
    recipe_ids = [1, 999, 1000]
    result = export_service.export_batch_recipes(recipe_ids)

    # 存在するレシピのみエクスポートされる
    assert result["recipe_count"] == 1


def test_import_result_model():
    """
    ImportResultモデルのテスト
    """
    result = ImportResult(
        success=True,
        imported_count=10,
        skipped_count=2,
        failed_count=1,
        details=[
            {"index": 0, "status": "imported"},
            {"index": 1, "status": "skipped"},
        ],
    )

    assert result.success is True
    assert result.imported_count == 10
    assert len(result.details) == 2


def test_validation_result_model():
    """
    ImportValidationResultモデルのテスト
    """
    result = ImportValidationResult(
        is_valid=True,
        total_recipes=10,
        valid_recipes=9,
        invalid_recipes=1,
        errors=[{"index": 5, "type": "validation_error"}],
        warnings=[],
        duplicates=[],
    )

    assert result.is_valid is True
    assert result.total_recipes == 10
    assert len(result.errors) == 1
