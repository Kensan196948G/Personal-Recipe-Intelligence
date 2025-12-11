"""
Collection API router for Personal Recipe Intelligence.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel, Field

from backend.models.collection import CollectionVisibility
from backend.services.collection_service import CollectionService

router = APIRouter(prefix="/api/v1/collection", tags=["collection"])

# Initialize service
collection_service = CollectionService()


# Request/Response models
class CreateCollectionRequest(BaseModel):
  """Request model for creating collection."""

  name: str = Field(..., min_length=1, max_length=100)
  description: Optional[str] = Field(None, max_length=500)
  visibility: CollectionVisibility = CollectionVisibility.PRIVATE
  tags: List[str] = Field(default_factory=list)


class UpdateCollectionRequest(BaseModel):
  """Request model for updating collection."""

  name: Optional[str] = Field(None, min_length=1, max_length=100)
  description: Optional[str] = Field(None, max_length=500)
  visibility: Optional[CollectionVisibility] = None
  tags: Optional[List[str]] = None


class AddRecipeRequest(BaseModel):
  """Request model for adding recipe to collection."""

  note: Optional[str] = Field(None, max_length=200)


class CopyCollectionRequest(BaseModel):
  """Request model for copying collection."""

  new_name: Optional[str] = Field(None, min_length=1, max_length=100)


class CollectionResponse(BaseModel):
  """Response model for collection."""

  status: str = "ok"
  data: dict
  error: Optional[str] = None


class CollectionListResponse(BaseModel):
  """Response model for collection list."""

  status: str = "ok"
  data: List[dict]
  error: Optional[str] = None


def get_user_id(authorization: Optional[str] = Header(None)) -> str:
  """
  Get user ID from authorization header.

  Args:
    authorization: Authorization header

  Returns:
    User ID

  Raises:
    HTTPException: If authorization header is missing or invalid
  """
  if not authorization:
    raise HTTPException(status_code=401, detail="Authorization header required")

  # Simple bearer token validation
  if not authorization.startswith("Bearer "):
    raise HTTPException(status_code=401, detail="Invalid authorization format")

  # Extract user ID from token (simplified - in production use JWT)
  token = authorization.replace("Bearer ", "")
  if not token:
    raise HTTPException(status_code=401, detail="Invalid token")

  # For now, use token as user ID (in production, decode JWT)
  return token


@router.post("", response_model=CollectionResponse)
async def create_collection(
  request: CreateCollectionRequest, authorization: Optional[str] = Header(None)
):
  """
  Create a new collection.

  Args:
    request: Collection creation request
    authorization: Authorization header

  Returns:
    Created collection
  """
  try:
    user_id = get_user_id(authorization)

    collection = collection_service.create_collection(
      name=request.name,
      owner_id=user_id,
      description=request.description,
      visibility=request.visibility,
      tags=request.tags,
    )

    return CollectionResponse(data=collection.to_dict())

  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to create collection: {str(e)}")


@router.get("", response_model=CollectionListResponse)
async def get_user_collections(authorization: Optional[str] = Header(None)):
  """
  Get all collections for current user.

  Args:
    authorization: Authorization header

  Returns:
    List of collections
  """
  try:
    user_id = get_user_id(authorization)
    collections = collection_service.get_user_collections(user_id)

    return CollectionListResponse(data=[c.to_dict() for c in collections])

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to get collections: {str(e)}")


@router.get("/public", response_model=CollectionListResponse)
async def get_public_collections(
  limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)
):
  """
  Get public collections.

  Args:
    limit: Maximum number of collections
    offset: Offset for pagination

  Returns:
    List of public collections
  """
  try:
    collections = collection_service.get_public_collections(limit=limit, offset=offset)

    return CollectionListResponse(data=[c.to_dict() for c in collections])

  except Exception as e:
    raise HTTPException(
      status_code=500, detail=f"Failed to get public collections: {str(e)}"
    )


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(
  collection_id: str, authorization: Optional[str] = Header(None)
):
  """
  Get collection by ID.

  Args:
    collection_id: Collection ID
    authorization: Authorization header

  Returns:
    Collection details
  """
  try:
    user_id = None
    try:
      user_id = get_user_id(authorization)
    except HTTPException:
      pass  # Allow anonymous access to public collections

    collection = collection_service.get_collection(collection_id, user_id)

    if not collection:
      raise HTTPException(status_code=404, detail="Collection not found")

    return CollectionResponse(data=collection.to_dict())

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to get collection: {str(e)}")


@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
  collection_id: str,
  request: UpdateCollectionRequest,
  authorization: Optional[str] = Header(None),
):
  """
  Update collection.

  Args:
    collection_id: Collection ID
    request: Collection update request
    authorization: Authorization header

  Returns:
    Updated collection
  """
  try:
    user_id = get_user_id(authorization)

    collection = collection_service.update_collection(
      collection_id=collection_id,
      user_id=user_id,
      name=request.name,
      description=request.description,
      visibility=request.visibility,
      tags=request.tags,
    )

    if not collection:
      raise HTTPException(status_code=404, detail="Collection not found")

    return CollectionResponse(data=collection.to_dict())

  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to update collection: {str(e)}")


@router.delete("/{collection_id}", response_model=CollectionResponse)
async def delete_collection(
  collection_id: str, authorization: Optional[str] = Header(None)
):
  """
  Delete collection.

  Args:
    collection_id: Collection ID
    authorization: Authorization header

  Returns:
    Success response
  """
  try:
    user_id = get_user_id(authorization)

    success = collection_service.delete_collection(collection_id, user_id)

    if not success:
      raise HTTPException(status_code=404, detail="Collection not found")

    return CollectionResponse(data={"message": "Collection deleted successfully"})

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to delete collection: {str(e)}")


@router.post("/{collection_id}/recipes/{recipe_id}", response_model=CollectionResponse)
async def add_recipe_to_collection(
  collection_id: str,
  recipe_id: str,
  request: AddRecipeRequest,
  authorization: Optional[str] = Header(None),
):
  """
  Add recipe to collection.

  Args:
    collection_id: Collection ID
    recipe_id: Recipe ID
    request: Add recipe request
    authorization: Authorization header

  Returns:
    Updated collection
  """
  try:
    user_id = get_user_id(authorization)

    collection = collection_service.add_recipe(
      collection_id=collection_id, recipe_id=recipe_id, user_id=user_id, note=request.note
    )

    if not collection:
      raise HTTPException(status_code=404, detail="Collection not found")

    return CollectionResponse(data=collection.to_dict())

  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to add recipe: {str(e)}")


@router.delete("/{collection_id}/recipes/{recipe_id}", response_model=CollectionResponse)
async def remove_recipe_from_collection(
  collection_id: str, recipe_id: str, authorization: Optional[str] = Header(None)
):
  """
  Remove recipe from collection.

  Args:
    collection_id: Collection ID
    recipe_id: Recipe ID
    authorization: Authorization header

  Returns:
    Updated collection
  """
  try:
    user_id = get_user_id(authorization)

    collection = collection_service.remove_recipe(collection_id, recipe_id, user_id)

    if not collection:
      raise HTTPException(status_code=404, detail="Collection not found")

    return CollectionResponse(data=collection.to_dict())

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to remove recipe: {str(e)}")


@router.post("/{collection_id}/copy", response_model=CollectionResponse)
async def copy_collection(
  collection_id: str,
  request: CopyCollectionRequest,
  authorization: Optional[str] = Header(None),
):
  """
  Copy collection.

  Args:
    collection_id: Collection ID to copy
    request: Copy request
    authorization: Authorization header

  Returns:
    Copied collection
  """
  try:
    user_id = get_user_id(authorization)

    collection = collection_service.copy_collection(
      collection_id=collection_id, user_id=user_id, new_name=request.new_name
    )

    if not collection:
      raise HTTPException(status_code=404, detail="Collection not found or not accessible")

    return CollectionResponse(data=collection.to_dict())

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to copy collection: {str(e)}")


@router.get("/stats/summary", response_model=CollectionResponse)
async def get_collection_stats():
  """
  Get collection statistics.

  Returns:
    Collection statistics
  """
  try:
    stats = collection_service.get_stats()

    return CollectionResponse(
      data={
        "total_collections": stats.total_collections,
        "public_collections": stats.public_collections,
        "private_collections": stats.private_collections,
        "total_recipes": stats.total_recipes,
        "most_popular_collection_id": stats.most_popular_collection_id,
      }
    )

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
