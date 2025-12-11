"""
レートリミッター使用例

各エンドポイントでのレートリミッター適用方法を示すサンプルルーター。
"""

from fastapi import APIRouter, Depends, Request
from typing import Dict, Any
from .rate_limiter import (
    general_rate_limit,
    ocr_rate_limit,
    translation_rate_limit,
    scraper_rate_limit,
    create_rate_limit_dependency,
)


# ルーター作成
router = APIRouter(prefix="/api/v1", tags=["examples"])


@router.get(
    "/recipes",
    dependencies=[Depends(general_rate_limit)],
    summary="レシピ一覧取得（一般API制限）",
)
async def get_recipes() -> Dict[str, Any]:
    """
    レシピ一覧を取得。

    レートリミット: 60リクエスト/分
    """
    return {"status": "ok", "data": {"recipes": [], "total": 0}, "error": None}


@router.post(
    "/recipes",
    dependencies=[Depends(general_rate_limit)],
    summary="レシピ作成（一般API制限）",
)
async def create_recipe(recipe_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    新規レシピを作成。

    レートリミット: 60リクエスト/分
    """
    return {"status": "ok", "data": {"id": "sample-id", "created": True}, "error": None}


@router.post(
    "/ocr/extract", dependencies=[Depends(ocr_rate_limit)], summary="OCR抽出（OCR制限）"
)
async def extract_ocr() -> Dict[str, Any]:
    """
    画像からテキストを抽出。

    レートリミット: 10リクエスト/分
    """
    return {
        "status": "ok",
        "data": {"text": "extracted text", "confidence": 0.95},
        "error": None,
    }


@router.post(
    "/translate",
    dependencies=[Depends(translation_rate_limit)],
    summary="翻訳（Translation制限）",
)
async def translate_text(text: str) -> Dict[str, Any]:
    """
    テキストを翻訳。

    レートリミット: 30リクエスト/分
    """
    return {
        "status": "ok",
        "data": {"original": text, "translated": "translated text"},
        "error": None,
    }


@router.post(
    "/scrape",
    dependencies=[Depends(scraper_rate_limit)],
    summary="スクレイピング（Scraper制限）",
)
async def scrape_url(url: str) -> Dict[str, Any]:
    """
    URLからレシピをスクレイピング。

    レートリミット: 20リクエスト/分
    """
    return {"status": "ok", "data": {"url": url, "recipe": {}}, "error": None}


@router.get(
    "/custom-limit",
    dependencies=[Depends(create_rate_limit_dependency(limit=5, window=60))],
    summary="カスタム制限（5リクエスト/分）",
)
async def custom_limit_endpoint() -> Dict[str, Any]:
    """
    カスタムレートリミットの例。

    レートリミット: 5リクエスト/分
    """
    return {
        "status": "ok",
        "data": {"message": "このエンドポイントは5リクエスト/分に制限されています"},
        "error": None,
    }


@router.get("/status", summary="ステータス確認（制限なし）")
async def get_status(request: Request) -> Dict[str, Any]:
    """
    APIステータスを確認。

    レートリミット: なし
    """
    return {
        "status": "ok",
        "data": {
            "api_status": "running",
            "version": "1.0.0",
            "client_ip": request.client.host if request.client else "unknown",
        },
        "error": None,
    }
