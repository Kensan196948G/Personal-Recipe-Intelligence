"""
Personal Recipe Intelligence - FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/")
async def root():
  """ルートエンドポイント"""
  return {"status": "ok", "message": "Personal Recipe Intelligence API"}


@app.get("/health")
async def health_check():
  """ヘルスチェック"""
  return {"status": "ok", "data": {"service": "healthy"}, "error": None}


@app.get("/api/v1/recipes")
async def get_recipes():
  """レシピ一覧取得"""
  return {"status": "ok", "data": [], "error": None}


@app.get("/api/v1/recipes/{recipe_id}")
async def get_recipe(recipe_id: int):
  """レシピ詳細取得"""
  return {"status": "ok", "data": {"id": recipe_id}, "error": None}
