"""
エクスポート強化APIルーター

複数フォーマットでのエクスポート、レシピブック生成、買い物リスト、栄養レポート、バックアップ機能を提供
"""

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

from backend.services.export_enhanced_service import ExportEnhancedService

router = APIRouter(prefix="/api/v1/export", tags=["export"])

# サービスインスタンス
export_service = ExportEnhancedService()


class ExportRequest(BaseModel):
    """エクスポートリクエスト"""

    recipe_ids: List[str] = Field(..., description="エクスポート対象レシピIDリスト")
    format: str = Field("json", description="エクスポートフォーマット")
    options: Optional[Dict[str, Any]] = Field(None, description="オプション設定")


class RecipeBookRequest(BaseModel):
    """レシピブックリクエスト"""

    recipe_ids: List[str] = Field(..., description="レシピIDリスト")
    title: Optional[str] = Field("レシピブック", description="ブックタイトル")
    theme: Optional[str] = Field("default", description="テーマ")
    options: Optional[Dict[str, Any]] = Field(None, description="オプション設定")


class ShoppingListRequest(BaseModel):
    """買い物リストリクエスト"""

    recipe_ids: List[str] = Field(..., description="レシピIDリスト")
    format: str = Field("markdown", description="エクスポートフォーマット")
    options: Optional[Dict[str, Any]] = Field(None, description="オプション設定")


class NutritionReportRequest(BaseModel):
    """栄養レポートリクエスト"""

    recipe_ids: List[str] = Field(..., description="レシピIDリスト")
    format: str = Field("json", description="エクスポートフォーマット")
    options: Optional[Dict[str, Any]] = Field(None, description="オプション設定")


class BackupRequest(BaseModel):
    """バックアップリクエスト"""

    metadata: Optional[Dict[str, Any]] = Field(None, description="メタデータ")


class RestoreRequest(BaseModel):
    """リストアリクエスト"""

    backup_file: str = Field(..., description="バックアップファイルパス")


def _load_recipes_from_storage(recipe_ids: List[str]) -> List[Dict[str, Any]]:
    """
    レシピをストレージから読み込み

    Args:
        recipe_ids: レシピIDリスト

    Returns:
        レシピデータのリスト

    Raises:
        HTTPException: レシピが見つからない場合
    """
    data_dir = Path("data")
    recipes_file = data_dir / "recipes.json"

    if not recipes_file.exists():
        raise HTTPException(status_code=404, detail="Recipes storage not found")

    with open(recipes_file, "r", encoding="utf-8") as f:
        all_recipes = json.load(f)

    # IDでフィルタリング
    if not recipe_ids:
        return all_recipes

    filtered_recipes = [r for r in all_recipes if r.get("id") in recipe_ids]

    if not filtered_recipes:
        raise HTTPException(status_code=404, detail="No recipes found with given IDs")

    return filtered_recipes


def _load_all_recipes() -> List[Dict[str, Any]]:
    """
    全レシピを読み込み

    Returns:
        全レシピデータのリスト
    """
    data_dir = Path("data")
    recipes_file = data_dir / "recipes.json"

    if not recipes_file.exists():
        return []

    with open(recipes_file, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/formats", response_model=Dict[str, Dict[str, str]])
async def get_supported_formats():
    """
    対応フォーマット一覧を取得

    Returns:
        対応フォーマット情報
    """
    return export_service.get_supported_formats()


@router.post("/recipes")
async def export_recipes(request: ExportRequest):
    """
    レシピをエクスポート

    Args:
        request: エクスポートリクエスト

    Returns:
        エクスポートデータ
    """
    try:
        # レシピを読み込み
        recipes = await asyncio.to_thread(
            _load_recipes_from_storage, request.recipe_ids
        )

        # エクスポート
        data = export_service.export_recipes(
            recipes=recipes, format_type=request.format, options=request.options
        )

        # レスポンス生成
        format_info = export_service.SUPPORTED_FORMATS.get(request.format, {})
        media_type = format_info.get("mime", "application/octet-stream")
        ext = format_info.get("ext", ".bin")

        return Response(
            content=data,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="recipes{ext}"',
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/recipe-book")
async def export_recipe_book(request: RecipeBookRequest):
    """
    レシピブックを生成（PDF）

    Args:
        request: レシピブックリクエスト

    Returns:
        PDFデータ
    """
    try:
        # レシピを読み込み
        recipes = await asyncio.to_thread(
            _load_recipes_from_storage, request.recipe_ids
        )

        # オプション設定
        options = request.options or {}
        options["title"] = request.title
        options["theme"] = request.theme

        # レシピブック生成
        data = export_service.export_recipe_book(recipes=recipes, options=options)

        return Response(
            content=data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="recipe_book.pdf"',
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Recipe book generation failed: {str(e)}"
        )


@router.post("/shopping-list")
async def export_shopping_list(request: ShoppingListRequest):
    """
    買い物リストをエクスポート

    Args:
        request: 買い物リストリクエスト

    Returns:
        買い物リストデータ
    """
    try:
        # レシピを読み込み
        recipes = await asyncio.to_thread(
            _load_recipes_from_storage, request.recipe_ids
        )

        # オプション設定
        options = request.options or {}
        options["format"] = request.format

        # 買い物リスト生成
        data = export_service.export_shopping_list(recipes=recipes, options=options)

        # レスポンス生成
        if request.format == "json":
            media_type = "application/json"
            ext = ".json"
        elif request.format == "markdown":
            media_type = "text/markdown"
            ext = ".md"
        else:
            media_type = "application/octet-stream"
            ext = ".txt"

        return Response(
            content=data,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="shopping_list{ext}"',
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Shopping list export failed: {str(e)}"
        )


@router.post("/nutrition-report")
async def export_nutrition_report(request: NutritionReportRequest):
    """
    栄養レポートをエクスポート

    Args:
        request: 栄養レポートリクエスト

    Returns:
        栄養レポートデータ
    """
    try:
        # レシピを読み込み
        recipes = await asyncio.to_thread(
            _load_recipes_from_storage, request.recipe_ids
        )

        # オプション設定
        options = request.options or {}
        options["format"] = request.format

        # 栄養レポート生成
        data = export_service.export_nutrition_report(recipes=recipes, options=options)

        # レスポンス生成
        if request.format == "json":
            media_type = "application/json"
            ext = ".json"
        elif request.format == "csv":
            media_type = "text/csv"
            ext = ".csv"
        else:
            media_type = "application/octet-stream"
            ext = ".txt"

        return Response(
            content=data,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="nutrition_report{ext}"',
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Nutrition report export failed: {str(e)}"
        )


@router.post("/backup")
async def create_backup(request: BackupRequest):
    """
    フルバックアップを作成

    Args:
        request: バックアップリクエスト

    Returns:
        バックアップ情報
    """
    try:
        # 全レシピを読み込み
        recipes = await asyncio.to_thread(_load_all_recipes)

        # バックアップ作成
        backup_file = export_service.create_backup(
            recipes=recipes, metadata=request.metadata
        )

        return {
            "status": "ok",
            "data": {
                "backup_file": backup_file,
                "recipe_count": len(recipes),
            },
            "error": None,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup creation failed: {str(e)}")


@router.post("/restore")
async def restore_backup(request: RestoreRequest):
    """
    バックアップからリストア

    Args:
        request: リストアリクエスト

    Returns:
        リストア結果
    """
    try:
        # バックアップをリストア
        backup_data = export_service.restore_backup(request.backup_file)

        # レシピデータを保存
        data_dir = Path("data")
        data_dir.mkdir(parents=True, exist_ok=True)
        recipes_file = data_dir / "recipes.json"

        await asyncio.to_thread(
            recipes_file.write_text,
            json.dumps(backup_data["recipes"], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return {
            "status": "ok",
            "data": {
                "restored_recipe_count": len(backup_data["recipes"]),
                "backup_created_at": backup_data.get("created_at"),
            },
            "error": None,
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")


@router.get("/backups")
async def list_backups():
    """
    バックアップ一覧を取得

    Returns:
        バックアップリスト
    """
    try:
        backups = export_service.list_backups()

        return {
            "status": "ok",
            "data": {"backups": backups, "count": len(backups)},
            "error": None,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")


def _load_recipes_from_database(
    recipe_ids: Optional[List[int]] = None, limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    データベースからレシピを読み込み

    Args:
        recipe_ids: レシピIDリスト（Noneの場合は全レシピ）
        limit: 取得件数制限

    Returns:
        レシピデータのリスト
    """
    conn = sqlite3.connect("data/db/database.db")
    cursor = conn.cursor()

    # レシピ基本情報取得
    if recipe_ids:
        placeholders = ",".join(["?" for _ in recipe_ids])
        query = f"SELECT id, title, description, servings, prep_time_minutes, cook_time_minutes, source_type FROM recipe WHERE id IN ({placeholders}) ORDER BY id DESC"
        cursor.execute(query, recipe_ids)
    else:
        query = "SELECT id, title, description, servings, prep_time_minutes, cook_time_minutes, source_type FROM recipe ORDER BY id DESC"
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query)

    recipes_raw = cursor.fetchall()
    recipes = []

    for r in recipes_raw:
        recipe_id, title, desc, servings, prep_time, cook_time, source = r

        # 材料取得
        cursor.execute(
            "SELECT name, amount, unit FROM ingredient WHERE recipe_id = ?", (recipe_id,)
        )
        ingredients = [
            {"name": i[0], "amount": str(i[1]) if i[1] else "", "unit": i[2] or ""}
            for i in cursor.fetchall()
        ]

        # 手順取得
        cursor.execute(
            'SELECT description FROM step WHERE recipe_id = ? ORDER BY "order"',
            (recipe_id,),
        )
        steps = [s[0] for s in cursor.fetchall()]

        # タグ取得
        cursor.execute(
            """
            SELECT t.name FROM tag t
            JOIN recipetag rt ON t.id = rt.tag_id
            WHERE rt.recipe_id = ?
        """,
            (recipe_id,),
        )
        tags = [t[0] for t in cursor.fetchall()]

        recipes.append(
            {
                "id": recipe_id,
                "title": title,
                "description": desc,
                "servings": servings,
                "cooking_time_minutes": (prep_time or 0) + (cook_time or 0)
                if (prep_time or cook_time)
                else None,
                "source_type": source,
                "ingredients": ingredients,
                "steps": steps,
                "tags": tags,
            }
        )

    conn.close()
    return recipes


@router.get("/recipes-markdown")
async def export_all_recipes_markdown(
    limit: Optional[int] = None,
    use_colors: bool = True,
    use_icons: bool = True,
):
    """
    全レシピをMarkdown形式でエクスポート（データベース版）

    Args:
        limit: 取得件数制限（指定なしで全件）
        use_colors: 色付きHTML使用
        use_icons: アイコン使用

    Returns:
        Markdownファイル
    """
    try:
        # データベースからレシピ取得
        recipes = await asyncio.to_thread(_load_recipes_from_database, None, limit)

        if not recipes:
            raise HTTPException(status_code=404, detail="No recipes found")

        # Markdownエクスポート
        options = {"use_colors": use_colors, "use_icons": use_icons}
        data = export_service.export_recipes(
            recipes=recipes, format_type="markdown", options=options
        )

        # ファイル名生成
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recipes_{timestamp}.md"

        return Response(
            content=data,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Export failed: {str(e)}"
        )


@router.get("/recipes-html")
async def export_all_recipes_html(
    limit: Optional[int] = None,
    use_colors: bool = True,
    use_icons: bool = True,
):
    """
    全レシピをHTML形式でエクスポート（絵文字完全対応）

    Args:
        limit: 取得件数制限
        use_colors: 色付き使用
        use_icons: アイコン使用

    Returns:
        HTMLファイル
    """
    try:
        # データベースからレシピ取得
        recipes = await asyncio.to_thread(_load_recipes_from_database, None, limit)

        if not recipes:
            raise HTTPException(status_code=404, detail="No recipes found")

        # Markdownエクスポート
        options = {"use_colors": use_colors, "use_icons": use_icons}
        md_data = export_service.export_recipes(
            recipes=recipes, format_type="markdown", options=options
        )

        # HTMLラッパー
        md_content = md_data.decode("utf-8")
        html_template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>レシピ集</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Segoe UI Emoji',
                         'Segoe UI Symbol', 'Noto Color Emoji', 'Hiragino Sans', sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
            background: #f5f5f5;
            line-height: 1.8;
        }}
        h1 {{ color: #333; font-size: 2.5em; margin-bottom: 30px; }}
        h2 {{ color: #444; margin-top: 50px; font-size: 2em; border-left: 5px solid #764ba2; padding-left: 15px; }}
        h3 {{ color: #555; font-size: 1.5em; margin-top: 30px; }}
        code {{ background: #f0f0f0; padding: 3px 8px; border-radius: 4px; }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 10px 0; font-size: 1.1em; }}
    </style>
</head>
<body>
{md_content}
</body>
</html>"""

        # ファイル名生成
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recipes_{timestamp}.html"

        return Response(
            content=html_template.encode("utf-8"),
            media_type="text/html; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
