"""
Follow Router - フォロー関連APIエンドポイント
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from backend.services.follow_service import FollowService

router = APIRouter(prefix="/api/v1/follow", tags=["follow"])


# レスポンスモデル
class FollowResponse(BaseModel):
    """フォローレスポンス"""

    status: str = Field(default="ok")
    data: dict
    error: Optional[str] = None


class FollowersResponse(BaseModel):
    """フォロワー一覧レスポンス"""

    status: str = Field(default="ok")
    data: dict
    error: Optional[str] = None


class FollowStatusResponse(BaseModel):
    """フォロー状態レスポンス"""

    status: str = Field(default="ok")
    data: dict
    error: Optional[str] = None


class FeedResponse(BaseModel):
    """フィードレスポンス"""

    status: str = Field(default="ok")
    data: list
    error: Optional[str] = None


class SuggestionsResponse(BaseModel):
    """おすすめユーザーレスポンス"""

    status: str = Field(default="ok")
    data: list
    error: Optional[str] = None


# 依存関係
def get_follow_service() -> FollowService:
    """フォローサービスのインスタンスを取得"""
    return FollowService()


def get_current_user_id() -> str:
    """
    現在のユーザーIDを取得（仮実装）

    TODO: 認証機能実装時に JWT トークンから取得するように変更
    """
    return "user_1"


@router.post("/{user_id}", response_model=FollowResponse)
async def follow_user(
    user_id: str,
    follow_service: FollowService = Depends(get_follow_service),
    current_user_id: str = Depends(get_current_user_id),
):
    """
    ユーザーをフォロー

    Args:
        user_id: フォロー対象のユーザーID

    Returns:
        フォロー関係データ
    """
    try:
        follow_data = follow_service.follow_user(current_user_id, user_id)
        return FollowResponse(status="ok", data=follow_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"フォロー処理に失敗しました: {str(e)}"
        )


@router.delete("/{user_id}", response_model=FollowResponse)
async def unfollow_user(
    user_id: str,
    follow_service: FollowService = Depends(get_follow_service),
    current_user_id: str = Depends(get_current_user_id),
):
    """
    ユーザーをアンフォロー

    Args:
        user_id: アンフォロー対象のユーザーID

    Returns:
        成功メッセージ
    """
    try:
        success = follow_service.unfollow_user(current_user_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="フォロー関係が存在しません")
        return FollowResponse(
            status="ok", data={"message": "アンフォローしました", "user_id": user_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"アンフォロー処理に失敗しました: {str(e)}"
        )


@router.get("/followers", response_model=FollowersResponse)
async def get_followers(
    user_id: Optional[str] = Query(None, description="対象ユーザーID（省略時は自分）"),
    limit: int = Query(100, ge=1, le=500, description="取得件数"),
    offset: int = Query(0, ge=0, description="オフセット"),
    follow_service: FollowService = Depends(get_follow_service),
    current_user_id: str = Depends(get_current_user_id),
):
    """
    フォロワー一覧を取得

    Args:
        user_id: 対象ユーザーID（省略時は現在のユーザー）
        limit: 取得件数
        offset: オフセット

    Returns:
        フォロワー一覧とメタデータ
    """
    try:
        target_user_id = user_id if user_id else current_user_id
        followers_data = follow_service.get_followers(target_user_id, limit, offset)
        return FollowersResponse(status="ok", data=followers_data)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"フォロワー取得に失敗しました: {str(e)}"
        )


@router.get("/following", response_model=FollowersResponse)
async def get_following(
    user_id: Optional[str] = Query(None, description="対象ユーザーID（省略時は自分）"),
    limit: int = Query(100, ge=1, le=500, description="取得件数"),
    offset: int = Query(0, ge=0, description="オフセット"),
    follow_service: FollowService = Depends(get_follow_service),
    current_user_id: str = Depends(get_current_user_id),
):
    """
    フォロー中ユーザー一覧を取得

    Args:
        user_id: 対象ユーザーID（省略時は現在のユーザー）
        limit: 取得件数
        offset: オフセット

    Returns:
        フォロー中ユーザー一覧とメタデータ
    """
    try:
        target_user_id = user_id if user_id else current_user_id
        following_data = follow_service.get_following(target_user_id, limit, offset)
        return FollowersResponse(status="ok", data=following_data)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"フォロー中ユーザー取得に失敗しました: {str(e)}"
        )


@router.get("/feed", response_model=FeedResponse)
async def get_follow_feed(
    limit: int = Query(20, ge=1, le=100, description="取得件数"),
    follow_service: FollowService = Depends(get_follow_service),
    current_user_id: str = Depends(get_current_user_id),
):
    """
    フォロー中ユーザーの新着レシピを取得

    Args:
        limit: 取得件数（デフォルト: 20）

    Returns:
        新着レシピリスト
    """
    try:
        feed = follow_service.get_follow_feed(current_user_id, limit)
        return FeedResponse(status="ok", data=feed)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"フィード取得に失敗しました: {str(e)}"
        )


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggested_users(
    limit: int = Query(10, ge=1, le=50, description="取得件数"),
    follow_service: FollowService = Depends(get_follow_service),
    current_user_id: str = Depends(get_current_user_id),
):
    """
    おすすめユーザーを取得

    Args:
        limit: 取得件数（デフォルト: 10）

    Returns:
        おすすめユーザーリスト
    """
    try:
        suggestions = follow_service.get_suggested_users(current_user_id, limit)
        return SuggestionsResponse(status="ok", data=suggestions)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"おすすめユーザー取得に失敗しました: {str(e)}"
        )


@router.get("/status/{user_id}", response_model=FollowStatusResponse)
async def get_follow_status(
    user_id: str,
    follow_service: FollowService = Depends(get_follow_service),
    current_user_id: str = Depends(get_current_user_id),
):
    """
    フォロー状態を確認

    Args:
        user_id: 対象ユーザーID

    Returns:
        フォロー状態情報
    """
    try:
        status = follow_service.get_follow_status(current_user_id, user_id)
        return FollowStatusResponse(status="ok", data=status)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"フォロー状態取得に失敗しました: {str(e)}"
        )
