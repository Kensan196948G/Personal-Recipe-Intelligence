"""
Personal Recipe Intelligence - FastAPI Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import (
    cache_router,
    nutrition_router,
    ocr_router,
    recipes_router,
    scraper_router,
    search_router,
    shopping_list_router,
    tags_router,
    translation_router,
)
from backend.api.routers.csv_import import router as csv_import_router
from backend.api.routers.collector import router as collector_router

app = FastAPI(
    title="Personal Recipe Intelligence API",
    description="個人向け料理レシピ収集・解析・管理システム",
    version="0.1.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://192.168.0.29:3000",
        "http://192.168.0.29:5173",
        "http://192.168.0.187:5173",
        "http://192.168.0.187:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(recipes_router)
app.include_router(tags_router)
app.include_router(scraper_router)
app.include_router(ocr_router)
app.include_router(translation_router)
app.include_router(search_router)
app.include_router(nutrition_router)
app.include_router(cache_router)
app.include_router(csv_import_router)
app.include_router(collector_router)
app.include_router(shopping_list_router)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"status": "ok", "message": "Personal Recipe Intelligence API"}


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok", "data": {"service": "healthy"}, "error": None}
