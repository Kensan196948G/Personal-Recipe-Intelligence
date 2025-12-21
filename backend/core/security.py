"""
Personal Recipe Intelligence - Security Utilities

セキュリティ関連のユーティリティ関数。
CLAUDE.md Section 5準拠。
"""

import re
import uuid
import logging
from pathlib import Path
from typing import Optional, Tuple
from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)

# ファイルアップロード設定
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# ファイルのマジックバイト（ヘッダー）
MAGIC_BYTES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"GIF87a": "image/gif",
    b"GIF89a": "image/gif",
    b"RIFF": "image/webp",  # WebP (RIFF header)
}


def detect_mime_type(content: bytes) -> Optional[str]:
    """
    ファイルのマジックバイトからMIMEタイプを検出

    Args:
        content: ファイルの先頭バイト

    Returns:
        検出されたMIMEタイプ、または None
    """
    for magic, mime in MAGIC_BYTES.items():
        if content.startswith(magic):
            return mime
    # WebPの追加チェック（RIFF....WEBP）
    if content[:4] == b"RIFF" and len(content) > 12 and content[8:12] == b"WEBP":
        return "image/webp"
    return None


def sanitize_filename(filename: str) -> str:
    """
    ファイル名をサニタイズ

    パストラバーサル攻撃を防ぐため、危険な文字を除去。

    Args:
        filename: 元のファイル名

    Returns:
        サニタイズされたファイル名
    """
    if not filename:
        return f"{uuid.uuid4().hex}.bin"

    # パス区切り文字を除去
    filename = filename.replace("/", "").replace("\\", "")
    # 危険な文字を除去
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
    # 連続ドットを除去（..を防ぐ）
    filename = re.sub(r"\.\.+", ".", filename)
    # 先頭のドットを除去
    filename = filename.lstrip(".")

    if not filename:
        return f"{uuid.uuid4().hex}.bin"

    # 長さ制限
    name, ext = (filename.rsplit(".", 1) + [""])[:2]
    name = name[:50]
    ext = ext[:10] if ext else ""

    return f"{uuid.uuid4().hex}_{name}.{ext}" if ext else f"{uuid.uuid4().hex}_{name}"


async def validate_image_upload(
    file: UploadFile,
    max_size: int = MAX_FILE_SIZE
) -> Tuple[bytes, str]:
    """
    画像アップロードを検証

    Args:
        file: アップロードされたファイル
        max_size: 最大ファイルサイズ（バイト）

    Returns:
        (ファイル内容, サニタイズされたファイル名) のタプル

    Raises:
        HTTPException: 検証エラー時
    """
    # ファイル内容を読み取り
    content = await file.read()

    # サイズチェック
    if len(content) > max_size:
        logger.warning(f"File upload rejected: size {len(content)} exceeds {max_size}")
        raise HTTPException(
            status_code=400,
            detail=f"ファイルサイズが大きすぎます（最大: {max_size // (1024 * 1024)}MB）"
        )

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="空のファイルです")

    # MIMEタイプをマジックバイトから検出（Content-Typeヘッダーは信頼しない）
    detected_mime = detect_mime_type(content)
    if detected_mime not in ALLOWED_IMAGE_MIME_TYPES:
        logger.warning(
            f"File upload rejected: invalid MIME type {detected_mime}, "
            f"content-type header was {file.content_type}"
        )
        raise HTTPException(
            status_code=400,
            detail="許可されていないファイル形式です。JPEG, PNG, GIF, WebPのみ対応しています。"
        )

    # 拡張子チェック
    ext = Path(file.filename or "").suffix.lower()
    if ext and ext not in ALLOWED_IMAGE_EXTENSIONS:
        logger.warning(f"File upload rejected: invalid extension {ext}")
        raise HTTPException(
            status_code=400,
            detail=f"許可されていない拡張子です: {ext}"
        )

    # ファイル名をサニタイズ
    safe_filename = sanitize_filename(file.filename or "upload")

    logger.info(f"File upload validated: {safe_filename}, size={len(content)}, mime={detected_mime}")

    return content, safe_filename


def mask_sensitive_data(data: str, show_chars: int = 4) -> str:
    """
    機密データをマスク

    Args:
        data: マスクするデータ
        show_chars: 末尾に表示する文字数

    Returns:
        マスクされたデータ
    """
    if not data:
        return "***"
    if len(data) <= show_chars:
        return "***"
    return f"***{data[-show_chars:]}"


def validate_path_parameter(param: str, param_name: str = "id") -> str:
    """
    パスパラメータを検証

    Args:
        param: 検証するパラメータ
        param_name: パラメータ名（エラーメッセージ用）

    Returns:
        検証済みパラメータ

    Raises:
        HTTPException: 検証エラー時
    """
    if not param:
        raise HTTPException(status_code=400, detail=f"{param_name}は必須です")

    # パストラバーサル攻撃を防ぐ
    if ".." in param or "/" in param or "\\" in param:
        logger.warning(f"Path traversal attempt detected: {param}")
        raise HTTPException(status_code=400, detail=f"不正な{param_name}です")

    # 長さ制限
    if len(param) > 255:
        raise HTTPException(status_code=400, detail=f"{param_name}が長すぎます")

    return param
