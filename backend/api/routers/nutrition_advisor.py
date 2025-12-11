"""
栄養士AI相談 APIルーター
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.services.nutrition_advisor_service import NutritionAdvisorService

router = APIRouter(prefix="/api/v1/advisor", tags=["nutrition-advisor"])

# サービスインスタンス
advisor_service = NutritionAdvisorService()


# リクエスト/レスポンスモデル
class ChatMessageRequest(BaseModel):
  """チャットメッセージリクエスト"""

  user_id: str = Field(..., description="ユーザーID")
  message: str = Field(..., min_length=1, max_length=1000, description="メッセージ")
  context: Optional[Dict[str, Any]] = Field(None, description="コンテキスト情報")


class ChatMessageResponse(BaseModel):
  """チャットメッセージレスポンス"""

  status: str
  data: Dict[str, Any]
  error: Optional[str] = None


class ChatHistoryResponse(BaseModel):
  """チャット履歴レスポンス"""

  status: str
  data: Dict[str, Any]
  error: Optional[str] = None


class MealAnalysisRequest(BaseModel):
  """食事分析リクエスト"""

  user_id: str = Field(..., description="ユーザーID")
  meal_type: str = Field(
    ..., description="食事タイプ", pattern="^(breakfast|lunch|dinner|snack|meal)$"
  )
  items: List[Dict[str, Any]] = Field(
    ..., description="食事アイテム（recipe_id, servings等）"
  )


class MealAnalysisResponse(BaseModel):
  """食事分析レスポンス"""

  status: str
  data: Dict[str, Any]
  error: Optional[str] = None


class DailyTipResponse(BaseModel):
  """今日のワンポイントレスポンス"""

  status: str
  data: Dict[str, Any]
  error: Optional[str] = None


class MealPlanRequest(BaseModel):
  """食事プランリクエスト"""

  user_id: str = Field(..., description="ユーザーID")
  target_calories: Optional[int] = Field(
    None, ge=1000, le=5000, description="目標カロリー"
  )
  goals: Optional[List[str]] = Field(None, description="目標（weight_loss, muscle_gain等）")
  restrictions: Optional[List[str]] = Field(
    None, description="制限事項（diabetes, allergy等）"
  )


class MealPlanResponse(BaseModel):
  """食事プランレスポンス"""

  status: str
  data: Dict[str, Any]
  error: Optional[str] = None


class UserProfileRequest(BaseModel):
  """ユーザープロファイル更新リクエスト"""

  preferences: Optional[Dict[str, Any]] = Field(None, description="設定")
  restrictions: Optional[List[str]] = Field(None, description="制限事項")
  goals: Optional[List[str]] = Field(None, description="目標")


class UserProfileResponse(BaseModel):
  """ユーザープロファイルレスポンス"""

  status: str
  data: Dict[str, Any]
  error: Optional[str] = None


class QuickActionsResponse(BaseModel):
  """クイックアクションレスポンス"""

  status: str
  data: List[Dict[str, str]]
  error: Optional[str] = None


# エンドポイント
@router.post("/chat", response_model=ChatMessageResponse)
async def chat_message(request: ChatMessageRequest):
  """
  チャットメッセージを送信

  Args:
    request: チャットメッセージリクエスト

  Returns:
    ChatMessageResponse: チャット応答
  """
  try:
    result = advisor_service.chat(
      user_id=request.user_id, message=request.message, context=request.context
    )

    return ChatMessageResponse(status="ok", data=result)

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"チャット処理エラー: {str(e)}")


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
  user_id: str = Query(..., description="ユーザーID"),
  limit: int = Query(50, ge=1, le=100, description="取得件数"),
  offset: int = Query(0, ge=0, description="オフセット"),
):
  """
  チャット履歴を取得

  Args:
    user_id: ユーザーID
    limit: 取得件数
    offset: オフセット

  Returns:
    ChatHistoryResponse: チャット履歴
  """
  try:
    result = advisor_service.get_chat_history(
      user_id=user_id, limit=limit, offset=offset
    )

    return ChatHistoryResponse(status="ok", data=result)

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"履歴取得エラー: {str(e)}")


@router.delete("/history")
async def clear_chat_history(user_id: str = Query(..., description="ユーザーID")):
  """
  チャット履歴をクリア

  Args:
    user_id: ユーザーID

  Returns:
    成功メッセージ
  """
  try:
    success = advisor_service.clear_chat_history(user_id=user_id)

    if not success:
      raise HTTPException(status_code=404, detail="ユーザーの履歴が見つかりません")

    return {"status": "ok", "data": {"message": "チャット履歴をクリアしました"}}

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"履歴クリアエラー: {str(e)}")


@router.post("/analyze", response_model=MealAnalysisResponse)
async def analyze_meal(request: MealAnalysisRequest):
  """
  食事を分析してアドバイスを提供

  Args:
    request: 食事分析リクエスト

  Returns:
    MealAnalysisResponse: 分析結果
  """
  try:
    meal_data = {"meal_type": request.meal_type, "items": request.items}

    result = advisor_service.analyze_meal(user_id=request.user_id, meal_data=meal_data)

    return MealAnalysisResponse(status="ok", data=result)

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"食事分析エラー: {str(e)}")


@router.get("/tips", response_model=DailyTipResponse)
async def get_daily_tip(user_id: Optional[str] = Query(None, description="ユーザーID")):
  """
  今日のワンポイントアドバイスを取得

  Args:
    user_id: ユーザーID（オプション）

  Returns:
    DailyTipResponse: 今日のワンポイント
  """
  try:
    result = advisor_service.get_daily_tip(user_id=user_id)

    return DailyTipResponse(status="ok", data=result)

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"ワンポイント取得エラー: {str(e)}")


@router.post("/meal-plan", response_model=MealPlanResponse)
async def generate_meal_plan(request: MealPlanRequest):
  """
  食事プランを提案

  Args:
    request: 食事プランリクエスト

  Returns:
    MealPlanResponse: 食事プラン
  """
  try:
    preferences = {}

    if request.target_calories:
      preferences["target_calories"] = request.target_calories

    if request.goals:
      preferences["goals"] = request.goals

    if request.restrictions:
      preferences["restrictions"] = request.restrictions

    result = advisor_service.generate_meal_plan(
      user_id=request.user_id, preferences=preferences
    )

    return MealPlanResponse(status="ok", data=result)

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"食事プラン生成エラー: {str(e)}")


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(user_id: str = Query(..., description="ユーザーID")):
  """
  ユーザープロファイルを取得

  Args:
    user_id: ユーザーID

  Returns:
    UserProfileResponse: ユーザープロファイル
  """
  try:
    profile = advisor_service.get_user_profile(user_id=user_id)

    if not profile:
      raise HTTPException(status_code=404, detail="ユーザープロファイルが見つかりません")

    return UserProfileResponse(status="ok", data=profile)

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"プロファイル取得エラー: {str(e)}")


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
  user_id: str = Query(..., description="ユーザーID"), request: UserProfileRequest = None
):
  """
  ユーザープロファイルを更新

  Args:
    user_id: ユーザーID
    request: プロファイル更新内容

  Returns:
    UserProfileResponse: 更新後のプロファイル
  """
  try:
    profile_updates = {}

    if request.preferences is not None:
      profile_updates["preferences"] = request.preferences

    if request.restrictions is not None:
      profile_updates["restrictions"] = request.restrictions

    if request.goals is not None:
      profile_updates["goals"] = request.goals

    profile = advisor_service.update_user_profile(
      user_id=user_id, profile_updates=profile_updates
    )

    return UserProfileResponse(status="ok", data=profile)

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"プロファイル更新エラー: {str(e)}")


@router.get("/quick-actions", response_model=QuickActionsResponse)
async def get_quick_actions():
  """
  クイックアクション一覧を取得

  Returns:
    QuickActionsResponse: クイックアクション
  """
  try:
    # サービスから直接クイックアクションを取得
    quick_actions = advisor_service.quick_actions

    return QuickActionsResponse(status="ok", data=quick_actions)

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"クイックアクション取得エラー: {str(e)}")
