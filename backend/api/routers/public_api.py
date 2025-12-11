"""
Public API Router

公開API管理用のエンドポイント
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional, List

from backend.services.api_key_service import (
  APIKeyService,
  APIKeyScope,
  RateLimit
)


router = APIRouter(prefix="/api/v1/public", tags=["Public API"])


# グローバルサービスインスタンス
_api_key_service: Optional[APIKeyService] = None


def get_api_key_service() -> APIKeyService:
  """APIキーサービスのインスタンスを取得"""
  global _api_key_service
  if _api_key_service is None:
    _api_key_service = APIKeyService()
  return _api_key_service


# リクエスト/レスポンスモデル

class CreateAPIKeyRequest(BaseModel):
  """APIキー作成リクエスト"""
  name: str = Field(..., min_length=1, max_length=100, description="キーの名前")
  read_recipes: bool = Field(True, description="レシピ読み取り権限")
  write_recipes: bool = Field(False, description="レシピ書き込み権限")
  delete_recipes: bool = Field(False, description="レシピ削除権限")
  read_tags: bool = Field(True, description="タグ読み取り権限")
  write_tags: bool = Field(False, description="タグ書き込み権限")
  requests_per_minute: int = Field(60, ge=1, le=1000, description="分あたりリクエスト数")
  requests_per_hour: int = Field(1000, ge=1, le=10000, description="時間あたりリクエスト数")
  requests_per_day: int = Field(10000, ge=1, le=100000, description="日あたりリクエスト数")


class APIKeyResponse(BaseModel):
  """APIキー情報レスポンス"""
  key_id: str
  name: str
  scope: dict
  rate_limit: dict
  created_at: str
  last_used_at: Optional[str]
  usage_count: int
  is_active: bool


class CreateAPIKeyResponse(BaseModel):
  """APIキー作成レスポンス"""
  api_key: str
  key_info: APIKeyResponse
  message: str = "API key created successfully. Please save this key securely as it won't be shown again."


class APIResponse(BaseModel):
  """標準APIレスポンス"""
  status: str
  data: Optional[dict] = None
  error: Optional[str] = None


# エンドポイント

@router.post(
  "/keys",
  response_model=APIResponse,
  status_code=status.HTTP_201_CREATED,
  summary="APIキーを発行"
)
async def create_api_key(
  request: CreateAPIKeyRequest,
  service: APIKeyService = Depends(get_api_key_service)
):
  """
  新しいAPIキーを発行

  - **name**: キーの識別名
  - **scope**: アクセス権限
  - **rate_limit**: レート制限設定

  生成されたAPIキーは一度しか表示されないため、安全に保存してください。
  """
  try:
    # スコープとレート制限を設定
    scope = APIKeyScope(
      read_recipes=request.read_recipes,
      write_recipes=request.write_recipes,
      delete_recipes=request.delete_recipes,
      read_tags=request.read_tags,
      write_tags=request.write_tags
    )

    rate_limit = RateLimit(
      requests_per_minute=request.requests_per_minute,
      requests_per_hour=request.requests_per_hour,
      requests_per_day=request.requests_per_day
    )

    # APIキー生成
    api_key, key_info = service.generate_api_key(
      name=request.name,
      scope=scope,
      rate_limit=rate_limit
    )

    # レスポンス作成（ハッシュは除外）
    key_response = APIKeyResponse(
      key_id=key_info.key_id,
      name=key_info.name,
      scope={
        "read_recipes": key_info.scope.read_recipes,
        "write_recipes": key_info.scope.write_recipes,
        "delete_recipes": key_info.scope.delete_recipes,
        "read_tags": key_info.scope.read_tags,
        "write_tags": key_info.scope.write_tags
      },
      rate_limit={
        "requests_per_minute": key_info.rate_limit.requests_per_minute,
        "requests_per_hour": key_info.rate_limit.requests_per_hour,
        "requests_per_day": key_info.rate_limit.requests_per_day
      },
      created_at=key_info.created_at,
      last_used_at=key_info.last_used_at,
      usage_count=key_info.usage_count,
      is_active=key_info.is_active
    )

    return APIResponse(
      status="ok",
      data={
        "api_key": api_key,
        "key_info": key_response.dict(),
        "message": "API key created successfully. Please save this key securely as it won't be shown again."
      }
    )

  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Failed to create API key: {str(e)}"
    )


@router.get(
  "/keys",
  response_model=APIResponse,
  summary="APIキー一覧を取得"
)
async def list_api_keys(
  service: APIKeyService = Depends(get_api_key_service)
):
  """
  登録されているすべてのAPIキーを取得

  セキュリティのため、実際のキー文字列やハッシュは含まれません。
  """
  try:
    keys = service.list_api_keys()

    return APIResponse(
      status="ok",
      data={
        "keys": keys,
        "total": len(keys)
      }
    )

  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Failed to list API keys: {str(e)}"
    )


@router.get(
  "/keys/{key_id}",
  response_model=APIResponse,
  summary="特定のAPIキー情報を取得"
)
async def get_api_key(
  key_id: str,
  service: APIKeyService = Depends(get_api_key_service)
):
  """
  指定されたキーIDのAPIキー情報を取得
  """
  if key_id not in service.keys:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="API key not found"
    )

  keys = service.list_api_keys()
  key_info = next((k for k in keys if k["key_id"] == key_id), None)

  return APIResponse(
    status="ok",
    data=key_info
  )


@router.delete(
  "/keys/{key_id}",
  response_model=APIResponse,
  summary="APIキーを削除"
)
async def delete_api_key(
  key_id: str,
  service: APIKeyService = Depends(get_api_key_service)
):
  """
  指定されたキーIDのAPIキーを完全に削除

  削除されたキーは復元できません。
  """
  success = service.delete_api_key(key_id)

  if not success:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="API key not found"
    )

  return APIResponse(
    status="ok",
    data={
      "message": "API key deleted successfully",
      "key_id": key_id
    }
  )


@router.patch(
  "/keys/{key_id}/revoke",
  response_model=APIResponse,
  summary="APIキーを無効化"
)
async def revoke_api_key(
  key_id: str,
  service: APIKeyService = Depends(get_api_key_service)
):
  """
  指定されたキーIDのAPIキーを無効化

  無効化されたキーは認証に使用できなくなりますが、情報は保持されます。
  """
  success = service.revoke_api_key(key_id)

  if not success:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="API key not found"
    )

  return APIResponse(
    status="ok",
    data={
      "message": "API key revoked successfully",
      "key_id": key_id
    }
  )


@router.post(
  "/keys/{key_id}/rotate",
  response_model=APIResponse,
  summary="APIキーをローテーション"
)
async def rotate_api_key(
  key_id: str,
  service: APIKeyService = Depends(get_api_key_service)
):
  """
  既存のAPIキーをローテーション

  新しいキーが生成され、古いキーは自動的に無効化されます。
  同じスコープとレート制限が新しいキーに適用されます。
  """
  result = service.rotate_api_key(key_id)

  if not result:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="API key not found"
    )

  new_api_key, new_key_info = result

  key_response = APIKeyResponse(
    key_id=new_key_info.key_id,
    name=new_key_info.name,
    scope={
      "read_recipes": new_key_info.scope.read_recipes,
      "write_recipes": new_key_info.scope.write_recipes,
      "delete_recipes": new_key_info.scope.delete_recipes,
      "read_tags": new_key_info.scope.read_tags,
      "write_tags": new_key_info.scope.write_tags
    },
    rate_limit={
      "requests_per_minute": new_key_info.rate_limit.requests_per_minute,
      "requests_per_hour": new_key_info.rate_limit.requests_per_hour,
      "requests_per_day": new_key_info.rate_limit.requests_per_day
    },
    created_at=new_key_info.created_at,
    last_used_at=new_key_info.last_used_at,
    usage_count=new_key_info.usage_count,
    is_active=new_key_info.is_active
  )

  return APIResponse(
    status="ok",
    data={
      "api_key": new_api_key,
      "key_info": key_response.dict(),
      "old_key_id": key_id,
      "message": "API key rotated successfully. Old key has been revoked."
    }
  )


@router.get(
  "/usage",
  response_model=APIResponse,
  summary="全体の使用量統計を取得"
)
async def get_overall_usage(
  service: APIKeyService = Depends(get_api_key_service)
):
  """
  すべてのAPIキーの使用量統計を取得
  """
  try:
    all_stats = []

    for key_id in service.keys.keys():
      stats = service.get_usage_stats(key_id)
      if stats:
        all_stats.append(stats)

    return APIResponse(
      status="ok",
      data={
        "usage_stats": all_stats,
        "total_keys": len(all_stats)
      }
    )

  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Failed to get usage stats: {str(e)}"
    )


@router.get(
  "/usage/{key_id}",
  response_model=APIResponse,
  summary="特定のAPIキーの使用量を取得"
)
async def get_key_usage(
  key_id: str,
  service: APIKeyService = Depends(get_api_key_service)
):
  """
  指定されたキーIDの使用量統計を取得

  - 現在の使用量（分/時/日）
  - レート制限情報
  - 残りリクエスト数
  """
  stats = service.get_usage_stats(key_id)

  if not stats:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="API key not found"
    )

  return APIResponse(
    status="ok",
    data=stats
  )


@router.get(
  "/docs",
  response_model=APIResponse,
  summary="API仕様ドキュメントを取得"
)
async def get_api_docs():
  """
  公開APIの使用方法とドキュメントを取得
  """
  docs = {
    "version": "1.0.0",
    "title": "Personal Recipe Intelligence Public API",
    "description": "レシピ管理システムの公開API",
    "authentication": {
      "type": "API Key",
      "header": "X-API-Key",
      "alternative": "Authorization: Bearer <api_key>"
    },
    "rate_limits": {
      "default": {
        "per_minute": 60,
        "per_hour": 1000,
        "per_day": 10000
      },
      "note": "レート制限はAPIキーごとに設定可能です"
    },
    "endpoints": {
      "recipes": {
        "GET /api/v1/recipes": "レシピ一覧取得",
        "GET /api/v1/recipes/{id}": "レシピ詳細取得",
        "POST /api/v1/recipes": "レシピ作成（書き込み権限必要）",
        "PUT /api/v1/recipes/{id}": "レシピ更新（書き込み権限必要）",
        "DELETE /api/v1/recipes/{id}": "レシピ削除（削除権限必要）"
      },
      "tags": {
        "GET /api/v1/tags": "タグ一覧取得",
        "POST /api/v1/tags": "タグ作成（書き込み権限必要）"
      }
    },
    "scopes": {
      "read_recipes": "レシピの読み取り",
      "write_recipes": "レシピの作成・更新",
      "delete_recipes": "レシピの削除",
      "read_tags": "タグの読み取り",
      "write_tags": "タグの作成・更新・削除"
    },
    "response_format": {
      "success": {
        "status": "ok",
        "data": {},
        "error": None
      },
      "error": {
        "status": "error",
        "data": None,
        "error": "error message"
      }
    },
    "example_usage": {
      "curl": "curl -H 'X-API-Key: your_api_key' https://api.example.com/api/v1/recipes",
      "python": "import requests\nheaders = {'X-API-Key': 'your_api_key'}\nresponse = requests.get('https://api.example.com/api/v1/recipes', headers=headers)"
    }
  }

  return APIResponse(
    status="ok",
    data=docs
  )
