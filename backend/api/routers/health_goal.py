"""
Health Goal API Router - 健康目標APIエンドポイント
"""

from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.health_goal_service import (
    HealthGoalService,
    Gender,
    ActivityLevel,
)


router = APIRouter(prefix="/api/v1/health-goal", tags=["health-goal"])
service = HealthGoalService()


# リクエストモデル
class ProfileRequest(BaseModel):
    """プロファイル設定リクエスト"""

    age: int = Field(..., ge=1, le=120, description="年齢")
    gender: Gender = Field(..., description="性別")
    weight: float = Field(..., gt=0, le=300, description="体重（kg）")
    height: float = Field(..., gt=0, le=300, description="身長（cm）")
    activity_level: ActivityLevel = Field(..., description="活動レベル")


class TargetsRequest(BaseModel):
    """目標設定リクエスト"""

    calories: float = Field(..., gt=0, description="カロリー（kcal）")
    protein: float = Field(..., gt=0, description="タンパク質（g）")
    fat: float = Field(..., gt=0, description="脂質（g）")
    carbohydrate: float = Field(..., gt=0, description="炭水化物（g）")
    fiber: float = Field(..., gt=0, description="食物繊維（g）")
    salt: float = Field(..., gt=0, description="塩分（g）")


class ProgressRequest(BaseModel):
    """達成率計算リクエスト"""

    nutrition_data: Dict[str, float] = Field(..., description="実際の摂取栄養データ")
    target_date: Optional[str] = Field(None, description="対象日（YYYY-MM-DD）")


# レスポンスモデル
class ProfileResponse(BaseModel):
    """プロファイルレスポンス"""

    status: str = "ok"
    data: Dict
    error: Optional[str] = None


class TargetsResponse(BaseModel):
    """目標値レスポンス"""

    status: str = "ok"
    data: Optional[Dict]
    error: Optional[str] = None


class RecommendationsResponse(BaseModel):
    """推奨値レスポンス"""

    status: str = "ok"
    data: Dict
    error: Optional[str] = None


class ProgressResponse(BaseModel):
    """達成率レスポンス"""

    status: str = "ok"
    data: Dict
    error: Optional[str] = None


class AdviceResponse(BaseModel):
    """アドバイスレスポンス"""

    status: str = "ok"
    data: List[Dict]
    error: Optional[str] = None


@router.post("/profile", response_model=ProfileResponse)
def set_profile(request: ProfileRequest):
    """
    プロファイルを設定

    Args:
      request: プロファイル設定リクエスト

    Returns:
      設定されたプロファイル
    """
    try:
        profile = service.set_profile(
            age=request.age,
            gender=request.gender,
            weight=request.weight,
            height=request.height,
            activity_level=request.activity_level,
        )
        return ProfileResponse(data=profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", response_model=ProfileResponse)
def get_profile():
    """
    プロファイルを取得

    Returns:
      保存されたプロファイル
    """
    try:
        profile = service.get_profile()
        if not profile:
            raise HTTPException(
                status_code=404, detail="プロファイルが設定されていません"
            )
        return ProfileResponse(data=profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/targets", response_model=TargetsResponse)
def set_targets(request: TargetsRequest):
    """
    目標値を設定

    Args:
      request: 目標設定リクエスト

    Returns:
      設定された目標値
    """
    try:
        targets = {
            "calories": request.calories,
            "protein": request.protein,
            "fat": request.fat,
            "carbohydrate": request.carbohydrate,
            "fiber": request.fiber,
            "salt": request.salt,
        }
        result = service.set_targets(targets)
        return TargetsResponse(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/targets", response_model=TargetsResponse)
def get_targets():
    """
    目標値を取得

    Returns:
      保存された目標値
    """
    try:
        targets = service.get_targets()
        return TargetsResponse(data=targets)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations", response_model=RecommendationsResponse)
def get_recommendations():
    """
    推奨値を取得

    Returns:
      プロファイルに基づく推奨栄養素摂取量
    """
    try:
        recommendations = service.get_recommendations()
        return RecommendationsResponse(data=recommendations)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/progress", response_model=ProgressResponse)
def calculate_progress(request: ProgressRequest):
    """
    達成率を計算

    Args:
      request: 達成率計算リクエスト

    Returns:
      達成率データ
    """
    try:
        target_date = None
        if request.target_date:
            target_date = datetime.strptime(request.target_date, "%Y-%m-%d").date()

        progress = service.calculate_progress(request.nutrition_data, target_date)
        return ProgressResponse(data=progress)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=ProgressResponse)
def get_history(days: int = 7):
    """
    達成率履歴を取得

    Args:
      days: 取得する日数

    Returns:
      履歴データ
    """
    try:
        history = service.get_history(days)
        return ProgressResponse(data={"history": history})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/advice", response_model=AdviceResponse)
def get_advice(request: ProgressRequest):
    """
    改善アドバイスを取得

    Args:
      request: 達成率計算リクエスト

    Returns:
      アドバイスリスト
    """
    try:
        target_date = None
        if request.target_date:
            target_date = datetime.strptime(request.target_date, "%Y-%m-%d").date()

        progress = service.calculate_progress(request.nutrition_data, target_date)
        advice = service.get_advice(progress)
        return AdviceResponse(data=advice)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
