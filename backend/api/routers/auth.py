"""
Authentication Router - 認証関連APIエンドポイント

JWT認証によるログイン・トークン発行機能
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

from backend.core.auth import (
    authenticate_user,
    create_access_token,
    get_current_user_id,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    """ログインリクエスト"""

    username: str = Field(..., description="ユーザー名")
    password: str = Field(..., description="パスワード")


class LoginResponse(BaseModel):
    """ログインレスポンス"""

    status: str = Field(default="ok")
    data: dict
    error: Optional[str] = None


class UserInfoResponse(BaseModel):
    """ユーザー情報レスポンス"""

    status: str = Field(default="ok")
    data: dict
    error: Optional[str] = None


@router.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """
    ログイン - JWTトークン発行

    Args:
        login_request: ユーザー名・パスワード

    Returns:
        JWTアクセストークン

    Raises:
        HTTPException: 認証失敗時
    """
    user = authenticate_user(login_request.username, login_request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # JWTトークン生成
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["user_id"]}, expires_delta=access_token_expires
    )

    return LoginResponse(
        status="ok",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
            "user_id": user["user_id"],
            "username": user["username"],
        },
    )


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(current_user_id: str = Depends(get_current_user_id)):
    """
    現在のユーザー情報取得

    Args:
        current_user_id: JWT認証から取得したユーザーID

    Returns:
        ユーザー情報
    """
    # TODO: 実際のユーザーデータベースから情報を取得
    # 現在はダミーデータを返す

    return UserInfoResponse(
        status="ok",
        data={
            "user_id": current_user_id,
            "username": f"user_{current_user_id}",
            "authenticated": True,
        },
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(current_user_id: str = Depends(get_current_user_id)):
    """
    トークンのリフレッシュ

    既存のトークンを使用して、新しいトークンを発行

    Args:
        current_user_id: 現在のユーザーID（JWT認証から取得）

    Returns:
        新しいJWTアクセストークン
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user_id}, expires_delta=access_token_expires
    )

    return LoginResponse(
        status="ok",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_id": current_user_id,
        },
    )
