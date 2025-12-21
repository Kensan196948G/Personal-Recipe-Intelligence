"""
栄養計算API サーバーの起動例

このスクリプトは栄養計算APIを含むFastAPIサーバーを起動します。

実行方法:
  python backend/main_nutrition_example.py

または:
  uvicorn backend.main_nutrition_example:app --reload --host 0.0.0.0 --port 8000

アクセス:
  - API: http://localhost:8000
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routers import nutrition

# FastAPI アプリケーション初期化
app = FastAPI(
    title="Personal Recipe Intelligence API",
    description="レシピ管理・栄養計算API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 栄養計算ルーターを登録
app.include_router(nutrition.router, tags=["Nutrition"])


# ルートエンドポイント
@app.get("/")
async def root():
    """
    APIルートエンドポイント
    """
    return {
        "message": "Personal Recipe Intelligence API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "nutrition": "/api/v1/nutrition",
        },
    }


# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    return {"status": "ok", "service": "nutrition-api"}


# API バージョン情報
@app.get("/api/v1")
async def api_info():
    """
    API バージョン情報
    """
    return {
        "version": "1.0.0",
        "endpoints": {
            "nutrition_calculate": "/api/v1/nutrition/calculate",
            "nutrition_ingredient": "/api/v1/nutrition/ingredient/{name}",
            "nutrition_search": "/api/v1/nutrition/search",
            "nutrition_list": "/api/v1/nutrition/ingredients",
        },
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Personal Recipe Intelligence - 栄養計算API")
    print("=" * 60)
    print("\n起動中...")
    print("\nアクセス先:")
    print("  - API: http://localhost:8000")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("\n停止: Ctrl+C")
    print("=" * 60)
    print()

    # サーバー起動
    uvicorn.run(
        "backend.main_nutrition_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
