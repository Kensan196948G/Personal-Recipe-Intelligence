"""
JWT Authentication Tests - JWT認証機能のテスト
"""

import pytest
from datetime import timedelta
from jose import jwt

from backend.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    authenticate_user,
    SECRET_KEY,
    ALGORITHM,
)


class TestPasswordHashing:
    """パスワードハッシング機能のテスト"""

    def test_hash_password(self):
        """パスワードがハッシュ化される"""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 50  # bcryptハッシュの長さ

    def test_verify_correct_password(self):
        """正しいパスワードが検証される"""
        password = "correct_password"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """間違ったパスワードが拒否される"""
        password = "correct_password"
        hashed = get_password_hash(password)

        assert verify_password("wrong_password", hashed) is False

    def test_different_passwords_generate_different_hashes(self):
        """異なるパスワードは異なるハッシュを生成"""
        password1 = "password1"
        password2 = "password2"

        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)

        assert hash1 != hash2


class TestJWTToken:
    """JWTトークン生成・検証のテスト"""

    def test_create_access_token(self):
        """アクセストークンが生成される"""
        data = {"sub": "user_123"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 100  # JWTトークンの長さ

    def test_decode_valid_token(self):
        """有効なトークンがデコードされる"""
        user_id = "test_user_456"
        token = create_access_token({"sub": user_id})

        payload = decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == user_id
        assert "exp" in payload  # 有効期限が含まれる

    def test_decode_invalid_token(self):
        """無効なトークンがNoneを返す"""
        invalid_token = "invalid.token.string"

        payload = decode_access_token(invalid_token)

        assert payload is None

    def test_token_with_custom_expiration(self):
        """カスタム有効期限でトークンが生成される"""
        user_id = "test_user"
        custom_expiration = timedelta(hours=2)
        token = create_access_token({"sub": user_id}, expires_delta=custom_expiration)

        # トークンをデコードして有効期限を確認
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["sub"] == user_id
        assert "exp" in payload

    def test_token_contains_correct_algorithm(self):
        """トークンが正しいアルゴリズムを使用"""
        token = create_access_token({"sub": "user_test"})

        # ヘッダーをデコード（検証なし）
        unverified_header = jwt.get_unverified_header(token)

        assert unverified_header["alg"] == ALGORITHM


class TestUserAuthentication:
    """ユーザー認証機能のテスト"""

    def test_authenticate_valid_user(self):
        """有効なユーザーが認証される"""
        user = authenticate_user("testuser", "testpass123")

        assert user is not None
        assert user["username"] == "testuser"
        assert user["user_id"] == "user_1"

    def test_authenticate_wrong_password(self):
        """間違ったパスワードで認証失敗"""
        user = authenticate_user("testuser", "wrong_password")

        assert user is None

    def test_authenticate_nonexistent_user(self):
        """存在しないユーザーで認証失敗"""
        user = authenticate_user("nonexistent", "any_password")

        assert user is None

    def test_authenticated_user_has_required_fields(self):
        """認証されたユーザーが必要なフィールドを持つ"""
        user = authenticate_user("testuser", "testpass123")

        assert user is not None
        assert "username" in user
        assert "user_id" in user
        assert "email" in user
        assert "hashed_password" in user


class TestSecurityFeatures:
    """セキュリティ機能のテスト"""

    def test_password_not_stored_in_plain_text(self):
        """パスワードが平文で保存されない"""
        user = authenticate_user("testuser", "testpass123")

        assert user is not None
        assert user["hashed_password"] != "testpass123"
        assert user["hashed_password"].startswith("$2b$")  # bcryptハッシュ

    def test_token_expiration_is_set(self):
        """トークンに有効期限が設定される"""
        token = create_access_token({"sub": "user_test"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert "exp" in payload
        assert payload["exp"] > 0

    def test_different_users_get_different_tokens(self):
        """異なるユーザーは異なるトークンを取得"""
        token1 = create_access_token({"sub": "user_1"})
        token2 = create_access_token({"sub": "user_2"})

        assert token1 != token2

        payload1 = decode_access_token(token1)
        payload2 = decode_access_token(token2)

        assert payload1["sub"] == "user_1"
        assert payload2["sub"] == "user_2"
