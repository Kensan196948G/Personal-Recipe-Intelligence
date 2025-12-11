"""
Recipe Sharing Router
レシピ共有APIエンドポイント
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

from backend.services.recipe_sharing_service import (
  RecipeSharingService,
  SharePermission,
  RecipeShare
)


router = APIRouter(prefix="/api/v1/sharing", tags=["sharing"])
sharing_service = RecipeSharingService()


# Pydantic Models
class CreateShareLinkRequest(BaseModel):
  """共有リンク作成リクエスト"""
  recipe_id: str = Field(..., description="レシピID")
  owner_id: str = Field(..., description="オーナーユーザーID")
  permission: SharePermission = Field(
    default=SharePermission.VIEW_ONLY,
    description="共有権限"
  )
  expires_in_days: int = Field(
    default=7,
    ge=0,
    le=365,
    description="有効期限（日数、0=無期限）"
  )
  shared_with: Optional[List[str]] = Field(
    default=None,
    description="共有相手リスト（メールアドレスまたはユーザーID）"
  )


class UpdateShareRequest(BaseModel):
  """共有情報更新リクエスト"""
  permission: Optional[SharePermission] = None
  expires_in_days: Optional[int] = Field(None, ge=0, le=365)
  shared_with: Optional[List[str]] = None


class InviteRequest(BaseModel):
  """招待送信リクエスト"""
  share_id: str = Field(..., description="共有ID")
  recipients: List[str] = Field(..., description="招待先リスト")
  message: Optional[str] = Field(None, description="メッセージ")


class ShareResponse(BaseModel):
  """共有情報レスポンス"""
  share_id: str
  recipe_id: str
  owner_id: str
  permission: str
  created_at: str
  expires_at: Optional[str]
  shared_with: List[str]
  share_link: str
  is_active: bool
  access_count: int
  last_accessed: Optional[str]


class ShareListResponse(BaseModel):
  """共有リストレスポンス"""
  shares: List[ShareResponse]
  total: int


class ShareStatsResponse(BaseModel):
  """共有統計レスポンス"""
  total_shares: int
  active_shares: int
  total_accesses: int
  view_only_shares: int
  edit_shares: int


class ShareHistoryResponse(BaseModel):
  """共有履歴レスポンス"""
  history: List[dict]
  total: int


def _to_share_response(share: RecipeShare) -> ShareResponse:
  """RecipeShareをShareResponseに変換"""
  return ShareResponse(
    share_id=share.share_id,
    recipe_id=share.recipe_id,
    owner_id=share.owner_id,
    permission=share.permission.value,
    created_at=share.created_at,
    expires_at=share.expires_at,
    shared_with=share.shared_with or [],
    share_link=share.share_link,
    is_active=share.is_active,
    access_count=share.access_count,
    last_accessed=share.last_accessed
  )


@router.post("/create-link", response_model=ShareResponse, status_code=status.HTTP_201_CREATED)
async def create_share_link(request: CreateShareLinkRequest):
  """
  共有リンクを作成

  Args:
    request: 共有リンク作成リクエスト

  Returns:
    ShareResponse: 作成された共有情報

  Raises:
    HTTPException: 作成失敗時
  """
  try:
    share = sharing_service.create_share_link(
      recipe_id=request.recipe_id,
      owner_id=request.owner_id,
      permission=request.permission,
      expires_in_days=request.expires_in_days,
      shared_with=request.shared_with
    )
    return _to_share_response(share)
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Failed to create share link: {str(e)}"
    )


@router.get("/link/{share_id}", response_model=ShareResponse)
async def get_share_by_link(share_id: str):
  """
  共有リンクでレシピ取得

  Args:
    share_id: 共有ID

  Returns:
    ShareResponse: 共有情報

  Raises:
    HTTPException: 共有が見つからない、または期限切れの場合
  """
  share = sharing_service.get_share_by_id(share_id)
  if not share:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Share not found or expired"
    )
  return _to_share_response(share)


@router.get("/recipe/{recipe_id}", response_model=ShareListResponse)
async def get_shares_by_recipe(recipe_id: str):
  """
  レシピの共有情報リストを取得

  Args:
    recipe_id: レシピID

  Returns:
    ShareListResponse: 共有リスト
  """
  shares = sharing_service.get_shares_by_recipe(recipe_id)
  return ShareListResponse(
    shares=[_to_share_response(share) for share in shares],
    total=len(shares)
  )


@router.get("/my-shares", response_model=ShareListResponse)
async def get_my_shares(owner_id: str):
  """
  自分が共有したレシピ一覧を取得

  Args:
    owner_id: オーナーユーザーID

  Returns:
    ShareListResponse: 共有リスト
  """
  shares = sharing_service.get_shares_by_owner(owner_id)
  return ShareListResponse(
    shares=[_to_share_response(share) for share in shares],
    total=len(shares)
  )


@router.get("/shared-with-me", response_model=ShareListResponse)
async def get_shared_with_me(user_id: str):
  """
  自分に共有されたレシピ一覧を取得

  Args:
    user_id: ユーザーID（メールアドレスまたはユーザーID）

  Returns:
    ShareListResponse: 共有リスト
  """
  shares = sharing_service.get_shares_with_user(user_id)
  return ShareListResponse(
    shares=[_to_share_response(share) for share in shares],
    total=len(shares)
  )


@router.put("/{share_id}", response_model=ShareResponse)
async def update_share(share_id: str, request: UpdateShareRequest):
  """
  共有情報を更新

  Args:
    share_id: 共有ID
    request: 更新リクエスト

  Returns:
    ShareResponse: 更新後の共有情報

  Raises:
    HTTPException: 更新失敗時
  """
  share = sharing_service.update_share(
    share_id=share_id,
    permission=request.permission,
    expires_in_days=request.expires_in_days,
    shared_with=request.shared_with
  )
  if not share:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Share not found"
    )
  return _to_share_response(share)


@router.delete("/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_share(share_id: str, user_id: str):
  """
  共有を解除

  Args:
    share_id: 共有ID
    user_id: 実行ユーザーID

  Raises:
    HTTPException: 解除失敗時
  """
  success = sharing_service.revoke_share(share_id, user_id)
  if not success:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Share not found or unauthorized"
    )


@router.post("/invite", status_code=status.HTTP_200_OK)
async def send_invite(request: InviteRequest):
  """
  招待を送信（実装は簡易版、実際のメール送信は含まない）

  Args:
    request: 招待リクエスト

  Returns:
    dict: 招待送信結果
  """
  # 共有情報の存在確認
  share = sharing_service.get_share_by_id(request.share_id)
  if not share:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Share not found"
    )

  # 実際のメール送信は別途実装が必要
  # ここでは招待先を shared_with に追加
  current_shared = share.shared_with or []
  new_shared = list(set(current_shared + request.recipients))

  updated_share = sharing_service.update_share(
    share_id=request.share_id,
    shared_with=new_shared
  )

  return {
    "status": "ok",
    "message": f"Invited {len(request.recipients)} recipients",
    "share_id": request.share_id,
    "recipients": request.recipients
  }


@router.get("/stats/{owner_id}", response_model=ShareStatsResponse)
async def get_share_stats(owner_id: str):
  """
  共有統計情報を取得

  Args:
    owner_id: オーナーユーザーID

  Returns:
    ShareStatsResponse: 統計情報
  """
  stats = sharing_service.get_share_stats(owner_id)
  return ShareStatsResponse(**stats)


@router.get("/history/{share_id}", response_model=ShareHistoryResponse)
async def get_share_history(share_id: str):
  """
  共有履歴を取得

  Args:
    share_id: 共有ID

  Returns:
    ShareHistoryResponse: 履歴情報
  """
  history = sharing_service.get_share_history(share_id)
  return ShareHistoryResponse(
    history=history,
    total=len(history)
  )


@router.post("/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_expired_shares():
  """
  期限切れの共有を無効化

  Returns:
    dict: 無効化結果
  """
  count = sharing_service.cleanup_expired_shares()
  return {
    "status": "ok",
    "message": f"Cleaned up {count} expired shares",
    "count": count
  }
