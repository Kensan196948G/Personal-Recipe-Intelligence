"""
Recipe API Router - Full CRUD operations for recipes
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

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
from backend.core.database import get_session
from backend.services.recipe_service import RecipeService

router = APIRouter(prefix="/api/v1/recipes", tags=["recipes"])


def get_recipe_service(session=Depends(get_session)) -> RecipeService:
  return RecipeService(session)


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
        created_at=r.created_at,
        tag_count=len(r.tags),
        ingredient_count=len(r.ingredients),
      )
    )

  total_pages = (total + per_page - 1) // per_page if total > 0 else 1

  return ApiResponse(
    status="ok",
    data=PaginatedResponse(
      items=[i.model_dump() for i in items],
      total=total,
      page=page,
      per_page=per_page,
      total_pages=total_pages,
    ).model_dump(),
  )


@router.get("/{recipe_id}", response_model=ApiResponse)
async def get_recipe(
  recipe_id: int,
  service: RecipeService = Depends(get_recipe_service),
):
  """レシピ詳細取得"""
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

  return ApiResponse(status="ok", data=recipe_data.model_dump())


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
    ingredients=[i.model_dump() for i in recipe_data.ingredients],
    steps=[s.model_dump() for s in recipe_data.steps],
    tag_ids=recipe_data.tag_ids,
  )

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
  )

  if not recipe:
    raise HTTPException(status_code=404, detail="Recipe not found")

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


@router.put(
  "/{recipe_id}/ingredients/{ingredient_id}", response_model=ApiResponse
)
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


@router.delete(
  "/{recipe_id}/ingredients/{ingredient_id}", response_model=ApiResponse
)
async def delete_ingredient(
  recipe_id: int,
  ingredient_id: int,
  service: RecipeService = Depends(get_recipe_service),
):
  """材料削除"""
  success = service.delete_ingredient(ingredient_id)
  if not success:
    raise HTTPException(status_code=404, detail="Ingredient not found")

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

  return ApiResponse(status="ok", data={"deleted": True})
