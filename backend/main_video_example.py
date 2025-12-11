"""
Personal Recipe Intelligence - FastAPI メインアプリケーション（Video統合版サンプル）
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import video

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# FastAPIアプリケーション作成
app = FastAPI(
    title="Personal Recipe Intelligence API",
    description="個人向けレシピ収集・解析・管理システム",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS設定（開発環境用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(video.router)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "service": "Personal Recipe Intelligence API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "video": "/api/v1/video",
        },
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "ok", "service": "personal-recipe-intelligence"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main_video_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
