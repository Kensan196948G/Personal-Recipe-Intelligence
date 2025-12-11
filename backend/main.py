"""
Personal Recipe Intelligence - FastAPI Backend

メインアプリケーションエントリポイント。
CLAUDE.md に準拠した API 設計・認証・エラーハンドリングを実装。
"""

import os
import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from middleware.auth_middleware import AuthMiddleware
from core.config import settings

# 環境変数読み込み
load_dotenv()

# ロギング設定（CLAUDE.md Section 6.2準拠）
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%S%z"
)
logger = logging.getLogger(__name__)

# アプリケーション設定
APP_VERSION = "1.0.0"
APP_TITLE = "Personal Recipe Intelligence API"
APP_DESCRIPTION = "個人向け料理レシピ収集・解析・管理システム"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションライフサイクル管理

    起動時・終了時の処理を定義。
    """
    # 起動時処理（JSON形式ログ）
    logger.info(f"Personal Recipe Intelligence API starting - Version: {APP_VERSION}, Environment: {settings.app_env}")

    # データディレクトリ確認
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)

    yield

    # 終了時処理
    logger.info("Personal Recipe Intelligence API shutting down")


# FastAPI アプリケーション
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS ミドルウェア（CLAUDE.md Section 5準拠 - セキュリティ強化）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # 設定ファイルから取得
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    max_age=3600,  # プリフライトキャッシュ
)

# 認証ミドルウェア追加
# /health, /docs, /openapi.json, /redoc は認証除外
app.add_middleware(
    AuthMiddleware,
    excluded_paths=["/health", "/docs", "/openapi.json", "/redoc", "/"],
)


# ============================================================
# ヘルスチェック（認証不要）
# ============================================================
@app.get(
    "/health",
    tags=["system"],
    summary="ヘルスチェック",
    response_model=dict,
)
async def health_check():
    """
    API ヘルスチェックエンドポイント（認証不要）

    Returns:
      dict: ステータス情報
    """
    return {
        "status": "ok",
        "data": {
            "service": "Personal Recipe Intelligence API",
            "version": APP_VERSION,
            "health": "healthy",
        },
        "error": None,
    }


@app.get(
    "/",
    tags=["system"],
    summary="ルートエンドポイント",
    response_model=dict,
)
async def root():
    """
    ルートエンドポイント（認証不要）

    Returns:
      dict: API 情報
    """
    return {
        "status": "ok",
        "data": {
            "message": "Personal Recipe Intelligence API",
            "version": APP_VERSION,
            "docs": "/docs",
        },
        "error": None,
    }


# ============================================================
# レシピ API（認証必要）
# ============================================================
@app.get(
    "/api/v1/recipes",
    tags=["recipes"],
    summary="レシピ一覧取得",
    response_model=dict,
)
async def get_recipes():
    """
    レシピ一覧を取得（認証必要）

    Returns:
      dict: レシピリスト
    """
    # TODO: データベースから取得
    return {
        "status": "ok",
        "data": {
            "recipes": [],
            "total": 0,
        },
        "error": None,
    }


@app.post(
    "/api/v1/recipes",
    tags=["recipes"],
    summary="レシピ作成",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe(request: Request):
    """
    新規レシピを作成（認証必要）

    Args:
      request: リクエストボディ

    Returns:
      dict: 作成されたレシピ情報
    """
    # TODO: リクエストボディをパース＆保存
    await request.json()

    return {
        "status": "ok",
        "data": {
            "message": "Recipe created successfully",
            "recipe_id": "sample_id",
        },
        "error": None,
    }


@app.get(
    "/api/v1/recipes/{recipe_id}",
    tags=["recipes"],
    summary="レシピ詳細取得",
    response_model=dict,
)
async def get_recipe(recipe_id: str):
    """
    レシピ詳細を取得（認証必要）

    Args:
      recipe_id: レシピID

    Returns:
      dict: レシピ詳細
    """
    # TODO: データベースから取得
    return {
        "status": "ok",
        "data": {
            "recipe_id": recipe_id,
            "title": "Sample Recipe",
            "ingredients": [],
            "steps": [],
        },
        "error": None,
    }


# ============================================================
# グローバルエラーハンドラ
# ============================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    グローバル例外ハンドラ

    Args:
      request: リクエスト
      exc: 例外

    Returns:
      JSONResponse: エラーレスポンス
    """
    # エラーID生成（追跡用）
    error_id = uuid.uuid4().hex[:12]

    # 内部ログに詳細を記録（CLAUDE.md Section 6準拠）
    logger.error(
        f"Error ID {error_id}: {str(exc)}",
        exc_info=True,
        extra={
            "error_id": error_id,
            "path": str(request.url.path),
            "method": request.method,
            "client_ip": request.client.host if request.client else "unknown"
        }
    )

    # セキュリティ: 本番環境では詳細なエラーメッセージを隠す
    if settings.debug:
        error_detail = str(exc)
    else:
        error_detail = f"Internal server error. Error ID: {error_id}"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "data": None,
            "error": error_detail,
            "error_id": error_id,
        },
    )


# ============================================================
# アプリケーション起動
# ============================================================
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info",
    )
