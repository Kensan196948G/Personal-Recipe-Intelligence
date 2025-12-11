"""
Personal Recipe Intelligence - FastAPI Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import recipes_router, tags_router

app = FastAPI(
    title="Personal Recipe Intelligence API",
    description="個人向け料理レシピ収集・解析・管理システム",
    version="0.1.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(recipes_router)
app.include_router(tags_router)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"status": "ok", "message": "Personal Recipe Intelligence API"}


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok", "data": {"service": "healthy"}, "error": None}
