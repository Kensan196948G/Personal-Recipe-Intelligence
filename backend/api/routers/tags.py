"""
Tag API Router - CRUD operations for tags
"""

from fastapi import APIRouter, Depends, HTTPException

from backend.api.schemas import ApiResponse, TagCreate, TagRead
from backend.core.database import get_session
from backend.services.recipe_service import TagService

router = APIRouter(prefix="/api/v1/tags", tags=["tags"])


def get_tag_service(session=Depends(get_session)) -> TagService:
    return TagService(session)


@router.get("", response_model=ApiResponse)
async def list_tags(service: TagService = Depends(get_tag_service)):
    """タグ一覧取得"""
    tags = service.get_tags()
    return ApiResponse(
        status="ok",
        data=[TagRead(id=t.id, name=t.name).model_dump() for t in tags],
    )


@router.get("/{tag_id}", response_model=ApiResponse)
async def get_tag(tag_id: int, service: TagService = Depends(get_tag_service)):
    """タグ取得"""
    tag = service.get_tag(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    return ApiResponse(status="ok", data=TagRead(id=tag.id, name=tag.name).model_dump())


@router.post("", response_model=ApiResponse, status_code=201)
async def create_tag(
    tag_data: TagCreate, service: TagService = Depends(get_tag_service)
):
    """タグ作成"""
    tag = service.create_tag(tag_data.name)
    return ApiResponse(status="ok", data=TagRead(id=tag.id, name=tag.name).model_dump())


@router.delete("/{tag_id}", response_model=ApiResponse)
async def delete_tag(tag_id: int, service: TagService = Depends(get_tag_service)):
    """タグ削除"""
    success = service.delete_tag(tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")

    return ApiResponse(status="ok", data={"deleted": True})
