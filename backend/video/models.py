"""
YouTube動画レシピのデータモデル定義
"""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class TimestampedStep(BaseModel):
    """タイムスタンプ付き手順"""

    step_number: int = Field(..., description="手順番号")
    description: str = Field(..., description="手順の説明")
    timestamp: Optional[str] = Field(None, description="タイムスタンプ (MM:SS 形式)")
    timestamp_seconds: Optional[int] = Field(None, description="タイムスタンプ（秒）")


class VideoRecipe(BaseModel):
    """動画から抽出したレシピデータ"""

    video_id: str = Field(..., description="YouTube動画ID")
    url: HttpUrl = Field(..., description="YouTube動画URL")
    title: str = Field(..., description="動画タイトル")
    description: Optional[str] = Field(None, description="動画説明文")
    channel: Optional[str] = Field(None, description="チャンネル名")
    duration: Optional[int] = Field(None, description="動画の長さ（秒）")
    thumbnail_url: Optional[str] = Field(None, description="サムネイル画像URL")

    # レシピ情報
    recipe_name: Optional[str] = Field(None, description="レシピ名")
    ingredients: List[str] = Field(default_factory=list, description="材料リスト")
    steps: List[TimestampedStep] = Field(
        default_factory=list, description="手順リスト（タイムスタンプ付き）"
    )
    servings: Optional[str] = Field(None, description="分量・人数")
    cooking_time: Optional[str] = Field(None, description="調理時間")
    tags: List[str] = Field(default_factory=list, description="タグリスト")

    # メタデータ
    has_transcript: bool = Field(default=False, description="字幕の有無")
    transcript_language: Optional[str] = Field(None, description="字幕言語")
    extracted_at: Optional[str] = Field(None, description="抽出日時 (ISO8601)")


class VideoExtractRequest(BaseModel):
    """動画レシピ抽出リクエスト"""

    url: str = Field(..., description="YouTube動画URL")
    language: str = Field(default="ja", description="優先字幕言語")
    extract_from_description: bool = Field(
        default=True, description="説明文からもレシピ情報を抽出するか"
    )


class VideoExtractResponse(BaseModel):
    """動画レシピ抽出レスポンス"""

    status: str = Field(..., description="処理ステータス")
    data: Optional[VideoRecipe] = Field(None, description="抽出されたレシピデータ")
    error: Optional[str] = Field(None, description="エラーメッセージ")
