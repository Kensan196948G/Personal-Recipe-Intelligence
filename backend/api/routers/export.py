"""
Export/Import API Router

レシピのエクスポート・インポートAPIエンドポイント
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.services.export_service import (
    ExportService,
)


router = APIRouter(prefix="/api/v1", tags=["export"])


# ========================================
# Request/Response Models
# ========================================


class BatchExportRequest(BaseModel):
    """
    バッチエクスポートリクエスト
    """

    recipe_ids: List[int] = Field(
        ..., min_items=1, description="エクスポートするレシピIDのリスト"
    )


class ImportRequest(BaseModel):
    """
    インポートリクエスト
    """

    data: Dict[str, Any] = Field(..., description="インポートするJSONデータ")
    skip_duplicates: bool = Field(default=True, description="重複をスキップするか")
    overwrite_duplicates: bool = Field(default=False, description="重複を上書きするか")


class ValidateImportRequest(BaseModel):
    """
    インポートバリデーションリクエスト
    """

    data: Dict[str, Any] = Field(..., description="検証するJSONデータ")
    check_duplicates: bool = Field(default=True, description="重複チェックを実行するか")


class ApiResponse(BaseModel):
    """
    標準APIレスポンス
    """

    status: str
    data: Optional[Any] = None
    error: Optional[str] = None


# ========================================
# Dependency Injection
# ========================================


def get_export_service():
    """
    ExportServiceのDI

    Returns:
        ExportService: エクスポートサービスインスタンス
    """
    # Get database session
    from backend.core.database import get_session

    db_session = next(get_session())
    return ExportService(db_session)


# ========================================
# Export Endpoints
# ========================================


@router.get("/export/recipes", response_model=ApiResponse)
async def export_all_recipes(
    export_service: ExportService = Depends(get_export_service),
    download: bool = Query(
        default=False, description="ファイルとしてダウンロードするか"
    ),
):
    """
    全レシピをJSON形式でエクスポート

    Args:
        export_service: エクスポートサービス
        download: ファイルダウンロードフラグ

    Returns:
        ApiResponse: エクスポートデータ
    """
    try:
        export_data = export_service.export_all_recipes()

        if download:
            # ファイルダウンロードレスポンスとして返す
            return JSONResponse(
                content=export_data,
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=recipes_export_{export_data['exported_at']}.json"
                },
            )

        return ApiResponse(status="ok", data=export_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/export/recipes/{recipe_id}", response_model=ApiResponse)
async def export_single_recipe(
    recipe_id: int,
    export_service: ExportService = Depends(get_export_service),
    download: bool = Query(
        default=False, description="ファイルとしてダウンロードするか"
    ),
):
    """
    単一レシピをJSON形式でエクスポート

    Args:
        recipe_id: レシピID
        export_service: エクスポートサービス
        download: ファイルダウンロードフラグ

    Returns:
        ApiResponse: エクスポートデータ

    Raises:
        HTTPException: レシピが見つからない場合
    """
    try:
        export_data = export_service.export_single_recipe(recipe_id)

        if download:
            return JSONResponse(
                content=export_data,
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=recipe_{recipe_id}_export.json"
                },
            )

        return ApiResponse(status="ok", data=export_data)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/export/recipes/batch", response_model=ApiResponse)
async def export_batch_recipes(
    request: BatchExportRequest,
    export_service: ExportService = Depends(get_export_service),
    download: bool = Query(
        default=False, description="ファイルとしてダウンロードするか"
    ),
):
    """
    選択したレシピ群をJSON形式でエクスポート

    Args:
        request: バッチエクスポートリクエスト
        export_service: エクスポートサービス
        download: ファイルダウンロードフラグ

    Returns:
        ApiResponse: エクスポートデータ
    """
    try:
        export_data = export_service.export_batch_recipes(request.recipe_ids)

        if download:
            return JSONResponse(
                content=export_data,
                media_type="application/json",
                headers={
                    "Content-Disposition": "attachment; filename=recipes_batch_export.json"
                },
            )

        return ApiResponse(status="ok", data=export_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch export failed: {str(e)}")


# ========================================
# Import Endpoints
# ========================================


@router.post("/import/validate", response_model=ApiResponse)
async def validate_import(
    request: ValidateImportRequest,
    export_service: ExportService = Depends(get_export_service),
):
    """
    インポート前のバリデーション

    Args:
        request: バリデーションリクエスト
        export_service: エクスポートサービス

    Returns:
        ApiResponse: バリデーション結果
    """
    try:
        validation_result = export_service.validate_import_data(
            request.data, check_duplicates=request.check_duplicates
        )

        return ApiResponse(status="ok", data=validation_result.model_dump())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/import/recipes", response_model=ApiResponse)
async def import_recipes(
    request: ImportRequest,
    export_service: ExportService = Depends(get_export_service),
):
    """
    JSONデータからレシピをインポート

    Args:
        request: インポートリクエスト
        export_service: エクスポートサービス

    Returns:
        ApiResponse: インポート結果
    """
    try:
        import_result = export_service.import_recipes(
            request.data,
            skip_duplicates=request.skip_duplicates,
            overwrite_duplicates=request.overwrite_duplicates,
        )

        if not import_result.success and import_result.imported_count == 0:
            return ApiResponse(
                status="error",
                error="Import failed",
                data=import_result.model_dump(),
            )

        return ApiResponse(status="ok", data=import_result.model_dump())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/import/recipes/file", response_model=ApiResponse)
async def import_recipes_from_file(
    file: UploadFile = File(..., description="インポートするJSONファイル"),
    skip_duplicates: bool = Query(default=True, description="重複をスキップするか"),
    overwrite_duplicates: bool = Query(default=False, description="重複を上書きするか"),
    export_service: ExportService = Depends(get_export_service),
):
    """
    アップロードされたJSONファイルからレシピをインポート

    Args:
        file: アップロードファイル
        skip_duplicates: 重複スキップフラグ
        overwrite_duplicates: 重複上書きフラグ
        export_service: エクスポートサービス

    Returns:
        ApiResponse: インポート結果
    """
    try:
        # ファイルの内容を読み込む
        content = await file.read()

        # JSON解析
        import json

        json_data = json.loads(content.decode("utf-8"))

        # インポート実行
        import_result = export_service.import_recipes(
            json_data,
            skip_duplicates=skip_duplicates,
            overwrite_duplicates=overwrite_duplicates,
        )

        if not import_result.success and import_result.imported_count == 0:
            return ApiResponse(
                status="error",
                error="Import failed",
                data=import_result.model_dump(),
            )

        return ApiResponse(status="ok", data=import_result.model_dump())

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File import failed: {str(e)}")


# ========================================
# Health Check
# ========================================


@router.get("/export/health", response_model=ApiResponse)
async def health_check():
    """
    エクスポート/インポート機能のヘルスチェック

    Returns:
        ApiResponse: ステータス
    """
    return ApiResponse(
        status="ok",
        data={
            "service": "export-import",
            "version": "1.0",
            "endpoints": [
                "GET /api/v1/export/recipes",
                "GET /api/v1/export/recipes/{recipe_id}",
                "POST /api/v1/export/recipes/batch",
                "POST /api/v1/import/validate",
                "POST /api/v1/import/recipes",
                "POST /api/v1/import/recipes/file",
            ],
        },
    )
