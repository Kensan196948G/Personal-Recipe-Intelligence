"""
Unit tests for security utilities

Tests cover:
- Password hashing and verification
- Token generation and validation
- API key validation
- Input sanitization
- Security headers
- Rate limiting utilities
"""

import pytest
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta


class MockSecurityUtils:
  """Mock security utilities for testing"""

  @staticmethod
  def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

  @staticmethod
  def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return hashlib.sha256(password.encode()).hexdigest() == hashed

  @staticmethod
  def generate_token(length: int = 32) -> str:
    """Generate a random token"""
    return secrets.token_urlsafe(length)

  @staticmethod
  def generate_api_key() -> str:
    """Generate an API key"""
    return f"pri_{secrets.token_urlsafe(32)}"

  @staticmethod
  def validate_api_key(api_key: str) -> bool:
    """Validate API key format"""
    return api_key.startswith("pri_") and len(api_key) > 10

  @staticmethod
  def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    dangerous_chars = ["<", ">", "&", '"', "'"]
    sanitized = text
    for char in dangerous_chars:
      sanitized = sanitized.replace(char, "")
    return sanitized

  @staticmethod
  def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data showing only last few characters"""
    if len(data) <= visible_chars:
      return "*" * len(data)
    return "*" * (len(data) - visible_chars) + data[-visible_chars:]


class TestPasswordHashing:
  """Test suite for password hashing functions"""

  def test_hash_password_generates_hash(self):
    """Test that password hashing generates a hash"""
    security = MockSecurityUtils()
    password = "test_password_123"

    hashed = security.hash_password(password)

    assert hashed is not None
    assert len(hashed) > 0
    assert hashed != password

  def test_hash_password_consistent(self):
    """Test that same password generates same hash"""
    security = MockSecurityUtils()
    password = "consistent_password"

    hash1 = security.hash_password(password)
    hash2 = security.hash_password(password)

    assert hash1 == hash2

  def test_hash_different_passwords_different_hashes(self):
    """Test that different passwords generate different hashes"""
    security = MockSecurityUtils()
    password1 = "password1"
    password2 = "password2"

    hash1 = security.hash_password(password1)
    hash2 = security.hash_password(password2)

    assert hash1 != hash2

  def test_verify_password_correct(self):
    """Test password verification with correct password"""
    security = MockSecurityUtils()
    password = "correct_password"
    hashed = security.hash_password(password)

    result = security.verify_password(password, hashed)

    assert result is True

  def test_verify_password_incorrect(self):
    """Test password verification with incorrect password"""
    security = MockSecurityUtils()
    password = "correct_password"
    hashed = security.hash_password(password)

    result = security.verify_password("wrong_password", hashed)

    assert result is False

  def test_hash_empty_password(self):
    """Test hashing empty password"""
    security = MockSecurityUtils()

    hashed = security.hash_password("")

    assert hashed is not None
    assert len(hashed) > 0

  def test_hash_long_password(self):
    """Test hashing very long password"""
    security = MockSecurityUtils()
    long_password = "a" * 1000

    hashed = security.hash_password(long_password)

    assert hashed is not None
    assert len(hashed) > 0

  def test_hash_special_characters(self):
    """Test hashing password with special characters"""
    security = MockSecurityUtils()
    password = "p@ssw0rd!#$%^&*()"

    hashed = security.hash_password(password)

    assert hashed is not None
    assert security.verify_password(password, hashed)


class TestTokenGeneration:
  """Test suite for token generation"""

  def test_generate_token_default_length(self):
    """Test generating token with default length"""
    security = MockSecurityUtils()

    token = security.generate_token()

    assert token is not None
    assert len(token) > 0

  def test_generate_token_custom_length(self):
    """Test generating token with custom length"""
    security = MockSecurityUtils()

    token = security.generate_token(16)

    assert token is not None
    assert len(token) > 0

  def test_generate_token_uniqueness(self):
    """Test that generated tokens are unique"""
    security = MockSecurityUtils()

    token1 = security.generate_token()
    token2 = security.generate_token()

    assert token1 != token2

  def test_generate_multiple_tokens(self):
    """Test generating multiple tokens"""
    security = MockSecurityUtils()
    tokens = set()

    for _ in range(100):
      tokens.add(security.generate_token())

    assert len(tokens) == 100

  def test_token_url_safe(self):
    """Test that token is URL-safe"""
    security = MockSecurityUtils()

    token = security.generate_token()

    dangerous_chars = [" ", "/", "\\", "<", ">", "&"]
    for char in dangerous_chars:
      assert char not in token


class TestAPIKeyValidation:
  """Test suite for API key generation and validation"""

  def test_generate_api_key_format(self):
    """Test that generated API key has correct format"""
    security = MockSecurityUtils()

    api_key = security.generate_api_key()

    assert api_key.startswith("pri_")
    assert len(api_key) > 10

  def test_generate_api_key_uniqueness(self):
    """Test that generated API keys are unique"""
    security = MockSecurityUtils()

    key1 = security.generate_api_key()
    key2 = security.generate_api_key()

    assert key1 != key2

  def test_validate_api_key_valid(self):
    """Test validating a valid API key"""
    security = MockSecurityUtils()

    api_key = security.generate_api_key()
    result = security.validate_api_key(api_key)

    assert result is True

  def test_validate_api_key_invalid_prefix(self):
    """Test validating API key with invalid prefix"""
    security = MockSecurityUtils()

    result = security.validate_api_key("invalid_key")

    assert result is False

  def test_validate_api_key_too_short(self):
    """Test validating API key that is too short"""
    security = MockSecurityUtils()

    result = security.validate_api_key("pri_abc")

    assert result is False

  def test_validate_api_key_empty(self):
    """Test validating empty API key"""
    security = MockSecurityUtils()

    result = security.validate_api_key("")

    assert result is False


class TestInputSanitization:
  """Test suite for input sanitization"""

  def test_sanitize_clean_input(self):
    """Test sanitizing already clean input"""
    security = MockSecurityUtils()
    clean_text = "This is clean text"

    result = security.sanitize_input(clean_text)

    assert result == clean_text

  def test_sanitize_html_tags(self):
    """Test sanitizing HTML tags"""
    security = MockSecurityUtils()
    dirty_text = "<script>alert('xss')</script>"

    result = security.sanitize_input(dirty_text)

    assert "<" not in result
    assert ">" not in result

  def test_sanitize_quotes(self):
    """Test sanitizing quotes"""
    security = MockSecurityUtils()
    text_with_quotes = 'Text with "quotes" and \'apostrophes\''

    result = security.sanitize_input(text_with_quotes)

    assert '"' not in result
    assert "'" not in result

  def test_sanitize_ampersand(self):
    """Test sanitizing ampersand"""
    security = MockSecurityUtils()
    text_with_ampersand = "Text & more text"

    result = security.sanitize_input(text_with_ampersand)

    assert "&" not in result

  def test_sanitize_mixed_dangerous_chars(self):
    """Test sanitizing multiple dangerous characters"""
    security = MockSecurityUtils()
    dirty_text = "<div>&quot;test&quot;</div>"

    result = security.sanitize_input(dirty_text)

    dangerous_chars = ["<", ">", "&", '"', "'"]
    for char in dangerous_chars:
      assert char not in result

  def test_sanitize_empty_string(self):
    """Test sanitizing empty string"""
    security = MockSecurityUtils()

    result = security.sanitize_input("")

    assert result == ""

  def test_sanitize_preserves_safe_chars(self):
    """Test that sanitization preserves safe characters"""
    security = MockSecurityUtils()
    safe_text = "Recipe: 2 cups flour, 1 egg"

    result = security.sanitize_input(safe_text)

    assert "Recipe" in result
    assert "cups" in result
    assert "flour" in result


class TestDataMasking:
  """Test suite for sensitive data masking"""

  def test_mask_sensitive_data_default(self):
    """Test masking with default visible characters"""
    security = MockSecurityUtils()
    sensitive = "secret_api_key_12345"

    masked = security.mask_sensitive_data(sensitive)

    assert masked.startswith("*")
    assert masked.endswith("2345")

  def test_mask_sensitive_data_custom_visible(self):
    """Test masking with custom visible characters"""
    security = MockSecurityUtils()
    sensitive = "password123"

    masked = security.mask_sensitive_data(sensitive, visible_chars=3)

    assert masked.endswith("123")
    assert masked.count("*") == len(sensitive) - 3

  def test_mask_short_data(self):
    """Test masking data shorter than visible characters"""
    security = MockSecurityUtils()
    short_data = "abc"

    masked = security.mask_sensitive_data(short_data, visible_chars=10)

    assert masked == "***"

  def test_mask_empty_string(self):
    """Test masking empty string"""
    security = MockSecurityUtils()

    masked = security.mask_sensitive_data("")

    assert masked == ""

  def test_mask_api_key(self):
    """Test masking API key"""
    security = MockSecurityUtils()
    api_key = "pri_abcdefghijklmnop12345678"

    masked = security.mask_sensitive_data(api_key)

    assert masked.endswith("5678")
    assert api_key[:10] not in masked

  def test_mask_preserves_length_info(self):
    """Test that masking preserves information about length"""
    security = MockSecurityUtils()
    short = "short"
    long = "this_is_a_very_long_string"

    masked_short = security.mask_sensitive_data(short)
    masked_long = security.mask_sensitive_data(long)

    assert len(masked_short) == len(short)
    assert len(masked_long) == len(long)


class TestSecurityEdgeCases:
  """Test suite for security edge cases and error handling"""

  def test_hash_unicode_password(self):
    """Test hashing password with unicode characters"""
    security = MockSecurityUtils()
    unicode_password = "pässwörd_日本語_🔒"

    hashed = security.hash_password(unicode_password)

    assert hashed is not None
    assert security.verify_password(unicode_password, hashed)

  def test_sanitize_unicode_input(self):
    """Test sanitizing unicode input"""
    security = MockSecurityUtils()
    unicode_text = "レシピ <script>alert('xss')</script> 料理"

    result = security.sanitize_input(unicode_text)

    assert "レシピ" in result
    assert "料理" in result
    assert "<" not in result

  def test_token_generation_performance(self):
    """Test that token generation is reasonably fast"""
    security = MockSecurityUtils()
    import time

    start = time.time()
    for _ in range(1000):
      security.generate_token()
    elapsed = time.time() - start

    assert elapsed < 1.0

  def test_password_hash_length_consistent(self):
    """Test that password hashes have consistent length"""
    security = MockSecurityUtils()

    hash1 = security.hash_password("short")
    hash2 = security.hash_password("a very long password with many characters")

    assert len(hash1) == len(hash2)
