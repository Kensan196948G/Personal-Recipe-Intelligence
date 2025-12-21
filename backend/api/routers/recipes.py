"""
Recipe API Router - Full CRUD operations for recipes
"""

from typing import Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from backend.api.schemas import (
    ApiResponse,
    IngredientCreate,
    IngredientRead,
    IngredientUpdate,
    PaginatedResponse,
    RecipeCreate,
    RecipeListItem,
    RecipeRead,
    RecipeUpdate,
    StepCreate,
    StepRead,
    StepUpdate,
    TagRead,
)
from backend.core.cache import get_cache, invalidate_cache
from backend.core.database import get_session
from backend.services.recipe_service import RecipeService
from config.cache_config import CacheConfig

router = APIRouter(prefix="/api/v1/recipes", tags=["recipes"])


def get_recipe_service(session=Depends(get_session)) -> RecipeService:
    return RecipeService(session)


def _recipe_list_cache_key(
    page: int,
    per_page: int,
    search: Optional[str],
    tag_id: Optional[int],
) -> str:
    search_key = search or ""
    tag_key = tag_id if tag_id is not None else ""
    return (
        f"{CacheConfig.PREFIX_RECIPES}:list:"
        f"page={page}:per_page={per_page}:search={search_key}:tag_id={tag_key}"
    )


def _recipe_detail_cache_key(recipe_id: int) -> str:
    return f"{CacheConfig.PREFIX_RECIPES}:detail:{recipe_id}"


def _invalidate_recipe_caches(recipe_id: Optional[int] = None) -> None:
    invalidate_cache(f"{CacheConfig.PREFIX_RECIPES}:")
    invalidate_cache(f"{CacheConfig.PREFIX_SEARCH}:")
    invalidate_cache(f"{CacheConfig.PREFIX_NUTRITION}:")
    if recipe_id is not None:
        invalidate_cache(_recipe_detail_cache_key(recipe_id))


# ===========================================
# Recipe CRUD
# ===========================================
@router.get("", response_model=ApiResponse)
async def list_recipes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=200),
    tag_id: Optional[int] = Query(None),
    service: RecipeService = Depends(get_recipe_service),
):
    """レシピ一覧取得"""
    cache = get_cache()
    cache_key = _recipe_list_cache_key(page, per_page, search, tag_id)
    cached_response = cache.get(cache_key)
    if cached_response is not None:
        return cached_response

    recipes, total = service.get_recipes(
        page=page, per_page=per_page, search=search, tag_id=tag_id
    )

    items = []
    for r in recipes:
        items.append(
            RecipeListItem(
                id=r.id,
                title=r.title,
                description=r.description,
                servings=r.servings,
                prep_time_minutes=r.prep_time_minutes,
                cook_time_minutes=r.cook_time_minutes,
                source_type=r.source_type,
                image_url=r.image_url,
                image_path=r.image_path,
                image_status=r.image_status,
                created_at=r.created_at,
                tag_count=len(r.tags),
                ingredient_count=len(r.ingredients),
            )
        )

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    response_payload = ApiResponse(
        status="ok",
        data=PaginatedResponse(
            items=[i.model_dump() for i in items],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        ).model_dump(),
    ).model_dump()

    cache.set(cache_key, response_payload, CacheConfig.TTL_RECIPE_LIST)
    return response_payload


@router.get("/{recipe_id}", response_model=ApiResponse)
async def get_recipe(
    recipe_id: int,
    service: RecipeService = Depends(get_recipe_service),
):
    """レシピ詳細取得"""
    cache = get_cache()
    cache_key = _recipe_detail_cache_key(recipe_id)
    cached_response = cache.get(cache_key)
    if cached_response is not None:
        return cached_response

    recipe = service.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe_data = RecipeRead(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        servings=recipe.servings,
        prep_time_minutes=recipe.prep_time_minutes,
        cook_time_minutes=recipe.cook_time_minutes,
        source_url=recipe.source_url,
        source_type=recipe.source_type,
        image_url=recipe.image_url,
        image_path=recipe.image_path,
        image_status=recipe.image_status,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
        ingredients=[
            IngredientRead(
                id=i.id,
                name=i.name,
                name_normalized=i.name_normalized,
                amount=i.amount,
                unit=i.unit,
                note=i.note,
                order=i.order,
            )
            for i in sorted(recipe.ingredients, key=lambda x: x.order)
        ],
        steps=[
            StepRead(id=s.id, description=s.description, order=s.order)
            for s in sorted(recipe.steps, key=lambda x: x.order)
        ],
        tags=[TagRead(id=rt.tag.id, name=rt.tag.name) for rt in recipe.tags if rt.tag],
    )

    response_payload = ApiResponse(
        status="ok", data=recipe_data.model_dump()
    ).model_dump()
    cache.set(cache_key, response_payload, CacheConfig.TTL_RECIPE_DETAIL)
    return response_payload


@router.post("", response_model=ApiResponse, status_code=201)
async def create_recipe(
    recipe_data: RecipeCreate,
    service: RecipeService = Depends(get_recipe_service),
):
    """レシピ作成"""
    recipe = service.create_recipe(
        title=recipe_data.title,
        description=recipe_data.description,
        servings=recipe_data.servings,
        prep_time_minutes=recipe_data.prep_time_minutes,
        cook_time_minutes=recipe_data.cook_time_minutes,
        source_url=recipe_data.source_url,
        source_type=recipe_data.source_type,
        image_url=recipe_data.image_url,
        ingredients=[i.model_dump() for i in recipe_data.ingredients],
        steps=[s.model_dump() for s in recipe_data.steps],
        tag_ids=recipe_data.tag_ids,
    )

    _invalidate_recipe_caches(recipe.id)
    return ApiResponse(status="ok", data={"id": recipe.id, "title": recipe.title})


@router.put("/{recipe_id}", response_model=ApiResponse)
async def update_recipe(
    recipe_id: int,
    recipe_data: RecipeUpdate,
    service: RecipeService = Depends(get_recipe_service),
):
    """レシピ更新"""
    recipe = service.update_recipe(
        recipe_id=recipe_id,
        title=recipe_data.title,
        description=recipe_data.description,
        servings=recipe_data.servings,
        prep_time_minutes=recipe_data.prep_time_minutes,
        cook_time_minutes=recipe_data.cook_time_minutes,
        source_url=recipe_data.source_url,
        source_type=recipe_data.source_type,
        image_url=recipe_data.image_url,
    )

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    _invalidate_recipe_caches(recipe.id)
    return ApiResponse(status="ok", data={"id": recipe.id, "title": recipe.title})


@router.delete("/{recipe_id}", response_model=ApiResponse)
async def delete_recipe(
    recipe_id: int,
    service: RecipeService = Depends(get_recipe_service),
):
    """レシピ削除"""
    success = service.delete_recipe(recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")

    _invalidate_recipe_caches(recipe_id)
    return ApiResponse(status="ok", data={"deleted": True})


# ===========================================
# Ingredient Operations
# ===========================================
@router.post("/{recipe_id}/ingredients", response_model=ApiResponse, status_code=201)
async def add_ingredient(
    recipe_id: int,
    ingredient_data: IngredientCreate,
    service: RecipeService = Depends(get_recipe_service),
):
    """材料追加"""
    ingredient = service.add_ingredient(recipe_id, ingredient_data.model_dump())
    if not ingredient:
        raise HTTPException(status_code=404, detail="Recipe not found")

    _invalidate_recipe_caches(recipe_id)
    return ApiResponse(
        status="ok",
        data=IngredientRead(
            id=ingredient.id,
            name=ingredient.name,
            name_normalized=ingredient.name_normalized,
            amount=ingredient.amount,
            unit=ingredient.unit,
            note=ingredient.note,
            order=ingredient.order,
        ).model_dump(),
    )


@router.put("/{recipe_id}/ingredients/{ingredient_id}", response_model=ApiResponse)
async def update_ingredient(
    recipe_id: int,
    ingredient_id: int,
    ingredient_data: IngredientUpdate,
    service: RecipeService = Depends(get_recipe_service),
):
    """材料更新"""
    ingredient = service.update_ingredient(
        ingredient_id, ingredient_data.model_dump(exclude_unset=True)
    )
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    _invalidate_recipe_caches(recipe_id)
    return ApiResponse(
        status="ok",
        data=IngredientRead(
            id=ingredient.id,
            name=ingredient.name,
            name_normalized=ingredient.name_normalized,
            amount=ingredient.amount,
            unit=ingredient.unit,
            note=ingredient.note,
            order=ingredient.order,
        ).model_dump(),
    )


@router.delete("/{recipe_id}/ingredients/{ingredient_id}", response_model=ApiResponse)
async def delete_ingredient(
    recipe_id: int,
    ingredient_id: int,
    service: RecipeService = Depends(get_recipe_service),
):
    """材料削除"""
    success = service.delete_ingredient(ingredient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    _invalidate_recipe_caches(recipe_id)
    return ApiResponse(status="ok", data={"deleted": True})


# ===========================================
# Step Operations
# ===========================================
@router.post("/{recipe_id}/steps", response_model=ApiResponse, status_code=201)
async def add_step(
    recipe_id: int,
    step_data: StepCreate,
    service: RecipeService = Depends(get_recipe_service),
):
    """手順追加"""
    step = service.add_step(recipe_id, step_data.model_dump())
    if not step:
        raise HTTPException(status_code=404, detail="Recipe not found")

    _invalidate_recipe_caches(recipe_id)
    return ApiResponse(
        status="ok",
        data=StepRead(
            id=step.id, description=step.description, order=step.order
        ).model_dump(),
    )


@router.put("/{recipe_id}/steps/{step_id}", response_model=ApiResponse)
async def update_step(
    recipe_id: int,
    step_id: int,
    step_data: StepUpdate,
    service: RecipeService = Depends(get_recipe_service),
):
    """手順更新"""
    step = service.update_step(step_id, step_data.model_dump(exclude_unset=True))
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    _invalidate_recipe_caches(recipe_id)
    return ApiResponse(
        status="ok",
        data=StepRead(
            id=step.id, description=step.description, order=step.order
        ).model_dump(),
    )


@router.delete("/{recipe_id}/steps/{step_id}", response_model=ApiResponse)
async def delete_step(
    recipe_id: int,
    step_id: int,
    service: RecipeService = Depends(get_recipe_service),
):
    """手順削除"""
    success = service.delete_step(step_id)
    if not success:
        raise HTTPException(status_code=404, detail="Step not found")

    _invalidate_recipe_caches(recipe_id)
    return ApiResponse(status="ok", data={"deleted": True})


# ===========================================
# Dashboard Statistics (認証不要)
# ===========================================
@router.get("/stats/dashboard", response_model=ApiResponse)
async def get_dashboard_stats(
    service: RecipeService = Depends(get_recipe_service),
):
    """ダッシュボード用統計情報を取得（認証不要）"""
    from datetime import datetime, timedelta

    cache = get_cache()
    cache_key = f"{CacheConfig.PREFIX_RECIPES}:dashboard_stats"
    cached_response = cache.get(cache_key)
    if cached_response is not None:
        return cached_response

    # 総レシピ数
    _, total_recipes = service.get_recipes(page=1, per_page=1)

    # 今週追加されたレシピ数
    week_ago = datetime.now() - timedelta(days=7)
    recipes_this_week = service.count_recipes_since(week_ago)

    # お気に入り数
    favorites_count = service.count_favorites()

    # タグ数
    tags_count = service.count_tags()

    # ソース別統計
    source_stats = service.get_source_type_stats()

    # 最近のレシピ（5件）
    recent_recipes, _ = service.get_recipes(page=1, per_page=5)
    recent_list = [
        {"id": r.id, "title": r.title, "source_type": r.source_type}
        for r in recent_recipes
    ]

    stats = {
        "total_recipes": total_recipes,
        "recipes_this_week": recipes_this_week,
        "favorites_count": favorites_count,
        "tags_count": tags_count,
        "source_stats": source_stats,
        "recent_recipes": recent_list,
    }

    response_payload = ApiResponse(status="ok", data=stats).model_dump()
    cache.set(cache_key, response_payload, 300)  # 5分キャッシュ
    return response_payload


# ===========================================
# Image Serving
# ===========================================
@router.get("/images/{filename}")
async def get_recipe_image(filename: str):
    """
    レシピ画像を配信

    Args:
        filename: 画像ファイル名

    Returns:
        画像ファイル
    """
    # ディレクトリトラバーサル対策
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # 画像パスを構築
    image_dir = Path("data/images")
    image_path = image_dir / filename

    # ファイルの存在確認
    if not image_path.exists() or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")

    # ディレクトリトラバーサル対策：絶対パスを確認
    abs_image_path = image_path.resolve()
    abs_image_dir = image_dir.resolve()

    if not str(abs_image_path).startswith(str(abs_image_dir)):
        raise HTTPException(status_code=400, detail="Invalid file path")

    # Content-Typeを拡張子から判定
    ext = image_path.suffix.lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }

    media_type = media_type_map.get(ext, "application/octet-stream")

    return FileResponse(
        path=str(abs_image_path), media_type=media_type, filename=filename
    )


# ===========================================
# Markdown Export
# ===========================================
def _recipe_to_markdown(recipe) -> str:
    """レシピをMarkdown形式に変換"""
    lines = []

    # タイトル
    lines.append(f"# {recipe.title}")
    lines.append("")

    # メタ情報
    if recipe.description:
        lines.append(f"> {recipe.description}")
        lines.append("")

    # 基本情報テーブル
    lines.append("| 項目 | 値 |")
    lines.append("|------|-----|")
    if recipe.servings:
        lines.append(f"| 人前 | {recipe.servings}人前 |")
    if recipe.prep_time_minutes:
        lines.append(f"| 準備時間 | {recipe.prep_time_minutes}分 |")
    if recipe.cook_time_minutes:
        lines.append(f"| 調理時間 | {recipe.cook_time_minutes}分 |")
    lines.append(f"| ソース | {recipe.source_type} |")
    lines.append("")

    # タグ
    if recipe.tags:
        tag_names = [rt.tag.name for rt in recipe.tags if rt.tag]
        if tag_names:
            lines.append(f"**タグ**: {', '.join(tag_names)}")
            lines.append("")

    # 材料
    lines.append("## 材料")
    lines.append("")
    if recipe.ingredients:
        for ing in sorted(recipe.ingredients, key=lambda x: x.order):
            amount_str = ""
            if ing.amount:
                amount_str = f"{ing.amount}"
            if ing.unit:
                amount_str += ing.unit
            note_str = f" ({ing.note})" if ing.note else ""
            lines.append(f"- {ing.name} {amount_str}{note_str}")
    else:
        lines.append("_材料が登録されていません_")
    lines.append("")

    # 手順
    lines.append("## 手順")
    lines.append("")
    if recipe.steps:
        for i, step in enumerate(sorted(recipe.steps, key=lambda x: x.order), 1):
            lines.append(f"{i}. {step.description}")
    else:
        lines.append("_手順が登録されていません_")
    lines.append("")

    # ソースURL
    if recipe.source_url:
        lines.append("---")
        lines.append(f"**出典**: [{recipe.source_url}]({recipe.source_url})")
        lines.append("")

    return "\n".join(lines)


@router.get("/{recipe_id}/export/markdown")
async def export_recipe_markdown(
    recipe_id: int,
    service: RecipeService = Depends(get_recipe_service),
):
    """
    レシピをMarkdown形式でエクスポート

    Args:
        recipe_id: レシピID

    Returns:
        Markdownファイル
    """
    from fastapi.responses import Response
    from urllib.parse import quote

    recipe = service.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    markdown_content = _recipe_to_markdown(recipe)

    # ファイル名をサニタイズ（日本語対応）
    safe_title = "".join(c for c in recipe.title if c.isalnum() or c in " _-　" or ord(c) > 127).strip()
    safe_title = safe_title[:50] if len(safe_title) > 50 else safe_title
    filename = f"{safe_title}.md"

    # RFC 5987形式でUTF-8エンコード（日本語ファイル名対応）
    encoded_filename = quote(filename, safe="")
    content_disposition = f"attachment; filename*=UTF-8''{encoded_filename}"

    return Response(
        content=markdown_content.encode("utf-8"),
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": content_disposition,
        },
    )
