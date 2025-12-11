"""
Search API Router - Enhanced recipe search endpoints
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend.api.schemas import ApiResponse, RecipeListItem
from backend.core.database import get_session

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("/recipes", response_model=ApiResponse)
async def search_recipes(
  q: Optional[str] = Query(None, description="検索クエリ"),
  ingredients: Optional[str] = Query(None, description="材料（カンマ区切り）"),
  fuzzy: bool = Query(False, description="あいまい検索を有効にする"),
  page: int = Query(1, ge=1),
  per_page: int = Query(20, ge=1, le=100),
  session=Depends(get_session),
):
  """レシピを検索（あいまい検索・材料検索対応）"""
  try:
    from backend.services.search_service import SearchService

    search_service = SearchService(session)

    # 材料リストをパース
    ingredient_list = None
    if ingredients:
      ingredient_list = [i.strip() for i in ingredients.split(",") if i.strip()]

    # 検索実行
    results, total = search_service.search(
      query=q,
      ingredients=ingredient_list,
      fuzzy=fuzzy,
      page=page,
      per_page=per_page,
    )

    # レスポンス整形
    items = []
    for r in results:
      items.append(
        RecipeListItem(
          id=r.id,
          title=r.title,
          description=r.description,
          servings=r.servings,
          prep_time_minutes=r.prep_time_minutes,
          cook_time_minutes=r.cook_time_minutes,
          source_type=r.source_type,
          created_at=r.created_at,
          tag_count=len(r.tags) if hasattr(r, "tags") else 0,
          ingredient_count=len(r.ingredients) if hasattr(r, "ingredients") else 0,
        ).model_dump()
      )

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return ApiResponse(
      status="ok",
      data={
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "query": q,
        "ingredients": ingredient_list,
        "fuzzy": fuzzy,
      },
    )

  except ImportError:
    # SearchServiceがない場合はフォールバック
    from backend.services.recipe_service import RecipeService

    service = RecipeService(session)
    recipes, total = service.get_recipes(page=page, per_page=per_page, search=q)

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
          created_at=r.created_at,
          tag_count=len(r.tags),
          ingredient_count=len(r.ingredients),
        ).model_dump()
      )

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return ApiResponse(
      status="ok",
      data={
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "query": q,
        "fuzzy": False,
      },
    )


@router.get("/by-ingredients", response_model=ApiResponse)
async def search_by_ingredients(
  ingredients: str = Query(..., description="材料（カンマ区切り）"),
  match_all: bool = Query(False, description="全ての材料を含むレシピのみ"),
  page: int = Query(1, ge=1),
  per_page: int = Query(20, ge=1, le=100),
  session=Depends(get_session),
):
  """材料からレシピを検索"""
  try:
    from backend.services.search_service import SearchService

    search_service = SearchService(session)

    # 材料リストをパース
    ingredient_list = [i.strip() for i in ingredients.split(",") if i.strip()]

    if not ingredient_list:
      return ApiResponse(
        status="ok",
        data={
          "items": [],
          "total": 0,
          "page": page,
          "per_page": per_page,
          "total_pages": 0,
        },
      )

    # 材料検索実行
    results, total = search_service.search_by_ingredients(
      ingredients=ingredient_list, match_all=match_all, page=page, per_page=per_page
    )

    items = []
    for r in results:
      items.append(
        RecipeListItem(
          id=r.id,
          title=r.title,
          description=r.description,
          servings=r.servings,
          prep_time_minutes=r.prep_time_minutes,
          cook_time_minutes=r.cook_time_minutes,
          source_type=r.source_type,
          created_at=r.created_at,
          tag_count=len(r.tags) if hasattr(r, "tags") else 0,
          ingredient_count=len(r.ingredients) if hasattr(r, "ingredients") else 0,
        ).model_dump()
      )

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return ApiResponse(
      status="ok",
      data={
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "ingredients": ingredient_list,
        "match_all": match_all,
      },
    )

  except ImportError:
    return ApiResponse(
      status="error",
      error={"code": "NOT_IMPLEMENTED", "message": "検索サービスが利用できません"},
    )


@router.get("/suggestions", response_model=ApiResponse)
async def get_search_suggestions(
  q: str = Query(..., min_length=1, description="検索クエリ"),
  limit: int = Query(10, ge=1, le=50),
  session=Depends(get_session),
):
  """検索候補を取得"""
  try:
    from backend.services.search_service import SearchService

    search_service = SearchService(session)
    suggestions = search_service.get_suggestions(query=q, limit=limit)

    return ApiResponse(status="ok", data={"suggestions": suggestions, "query": q})

  except ImportError:
    # フォールバック
    from sqlmodel import select

    from backend.models.recipe import Recipe

    stmt = select(Recipe.title).where(Recipe.title.contains(q)).limit(limit)
    results = session.exec(stmt).all()

    return ApiResponse(status="ok", data={"suggestions": list(results), "query": q})
