"""
CSV Import API Router - CSVインポート機能
"""

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from backend.api.schemas import ApiResponse
from backend.core.database import get_session
from backend.services.csv_import_service import CSVImportService

router = APIRouter(prefix="/api/v1/import", tags=["import"])


def get_csv_import_service(session=Depends(get_session)) -> CSVImportService:
    return CSVImportService(session)


@router.post("/csv", response_model=ApiResponse)
async def import_csv(
    file: UploadFile = File(...),
    skip_duplicates: bool = Query(True, description="重複レシピをスキップする"),
    service: CSVImportService = Depends(get_csv_import_service),
):
    """
    CSVファイルからレシピをインポート

    CSVフォーマット:
    - title (必須): レシピタイトル
    - description: 説明
    - servings: 人数
    - prep_time_minutes: 準備時間(分)
    - cook_time_minutes: 調理時間(分)
    - source_url: ソースURL
    - source_type: ソースタイプ (manual, web, ocr, csv)
    - ingredients: 材料 (フォーマット: "材料名:量:単位|材料名:量:単位")
    - steps: 手順 (フォーマット: "手順1|手順2|手順3")
    - tags: タグ (フォーマット: "タグ1,タグ2,タグ3")
    """
    # ファイルタイプチェック
    if not file.filename:
        raise HTTPException(status_code=400, detail="ファイル名が必要です")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSVファイルのみ対応しています")

    # ファイルサイズチェック (5MB制限)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400, detail="ファイルサイズは5MB以下にしてください"
        )

    # エンコーディング検出と変換
    try:
        # UTF-8で試す
        csv_content = content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            # Shift_JISで試す (日本語Excelでよく使われる)
            csv_content = content.decode("shift_jis")
        except UnicodeDecodeError:
            try:
                # CP932 (Windows日本語)で試す
                csv_content = content.decode("cp932")
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="ファイルのエンコーディングを認識できません。UTF-8またはShift_JISで保存してください",
                )

    # BOMを除去
    if csv_content.startswith("\ufeff"):
        csv_content = csv_content[1:]

    try:
        result = service.import_recipes(csv_content, skip_duplicates=skip_duplicates)
        return ApiResponse(status="ok", data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"インポートエラー: {str(e)}")


@router.post("/csv/preview", response_model=ApiResponse)
async def preview_csv(
    file: UploadFile = File(...),
    service: CSVImportService = Depends(get_csv_import_service),
):
    """
    CSVファイルのプレビュー（実際にはインポートしない）
    """
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSVファイルのみ対応しています")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400, detail="ファイルサイズは5MB以下にしてください"
        )

    try:
        csv_content = content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            csv_content = content.decode("shift_jis")
        except UnicodeDecodeError:
            try:
                csv_content = content.decode("cp932")
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="ファイルのエンコーディングを認識できません",
                )

    if csv_content.startswith("\ufeff"):
        csv_content = csv_content[1:]

    try:
        result = service.parse_csv(csv_content)
        return ApiResponse(
            status="ok",
            data={
                "recipes": result["recipes"][:10],  # プレビューは10件まで
                "total": len(result["recipes"]),
                "errors": result["errors"],
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/csv/template")
async def get_csv_template(
    service: CSVImportService = Depends(get_csv_import_service),
):
    """
    CSVテンプレートをダウンロード
    """
    csv_content = service.get_sample_csv()

    return Response(
        content=csv_content.encode("utf-8-sig"),  # BOM付きUTF-8 (Excel対応)
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=recipe_template.csv"},
    )


@router.get("/csv/format", response_model=ApiResponse)
async def get_csv_format():
    """
    CSVフォーマット仕様を取得
    """
    format_spec = {
        "columns": {
            "title": {"required": True, "description": "レシピタイトル", "example": "カレーライス"},
            "description": {
                "required": False,
                "description": "レシピの説明",
                "example": "家庭の定番カレー",
            },
            "servings": {"required": False, "description": "人数", "example": "4"},
            "prep_time_minutes": {
                "required": False,
                "description": "準備時間(分)",
                "example": "20",
            },
            "cook_time_minutes": {
                "required": False,
                "description": "調理時間(分)",
                "example": "40",
            },
            "source_url": {
                "required": False,
                "description": "ソースURL",
                "example": "https://example.com/recipe",
            },
            "source_type": {
                "required": False,
                "description": "ソースタイプ",
                "example": "manual",
                "allowed_values": ["manual", "web", "ocr", "csv"],
            },
            "ingredients": {
                "required": False,
                "description": "材料リスト",
                "format": "材料名:量:単位|材料名:量:単位",
                "example": "たまねぎ:2:個|にんじん:1:本",
            },
            "steps": {
                "required": False,
                "description": "調理手順",
                "format": "手順1|手順2|手順3",
                "example": "野菜を切る|肉を炒める|煮込む",
            },
            "tags": {
                "required": False,
                "description": "タグ",
                "format": "タグ1,タグ2,タグ3",
                "example": "和食,定番,簡単",
            },
        },
        "encoding": ["UTF-8", "UTF-8 with BOM", "Shift_JIS", "CP932"],
        "max_file_size": "5MB",
    }

    return ApiResponse(status="ok", data=format_spec)
