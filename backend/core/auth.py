"""
JWT Authentication Module
Personal Recipe Intelligence - セキュリティ認証システム
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# パスワードハッシング
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT設定
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev_secret_key_change_in_production_2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# HTTPBearer認証スキーム
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワード検証

    Args:
        plain_password: 平文パスワード
        hashed_password: ハッシュ化パスワード

    Returns:
        bool: 検証結果
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    パスワードハッシュ化

    Args:
        password: 平文パスワード

    Returns:
        str: ハッシュ化パスワード
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWTアクセストークン生成

    Args:
        data: トークンに含めるデータ（user_id等）
        expires_delta: 有効期限（デフォルト: 30分）

    Returns:
        str: JWTトークン
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    JWTトークンのデコード

    Args:
        token: JWTトークン

    Returns:
        Optional[dict]: デコードされたペイロード、無効な場合はNone
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    現在のユーザーIDを取得（JWT認証）

    Args:
        credentials: HTTPBearer認証情報

    Returns:
        str: ユーザーID

    Raises:
        HTTPException: 認証失敗時
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    現在のユーザーIDを取得（オプショナル）

    認証なしでもアクセス可能なエンドポイント用

    Args:
        credentials: HTTPBearer認証情報（オプション）

    Returns:
        Optional[str]: ユーザーID、認証なしの場合はNone
    """
    if credentials is None:
        return None

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


# ユーザー認証用のダミー関数（実際のユーザーDB実装後に置き換え）
def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    ユーザー認証（ダミー実装）

    TODO: 実際のユーザーデータベースと統合

    Args:
        username: ユーザー名
        password: パスワード

    Returns:
        Optional[dict]: ユーザー情報、認証失敗時はNone
    """
    # ダミーユーザー（開発用）
    fake_users_db = {
        "testuser": {
            "username": "testuser",
            "user_id": "user_1",
            "hashed_password": get_password_hash("testpass123"),
            "email": "test@example.com",
        }
    }

    user = fake_users_db.get(username)

    if not user:
        return None

    if not verify_password(password, user["hashed_password"]):
        return None

    return user
