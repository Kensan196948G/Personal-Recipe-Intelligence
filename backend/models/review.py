"""
Review data models for Personal Recipe Intelligence.
レビュー・評価のデータモデル定義
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass
class Rating:
  """星評価モデル"""

  score: int  # 1-5
  user_id: str
  recipe_id: str
  created_at: datetime = field(default_factory=datetime.now)

  def to_dict(self) -> dict:
    """辞書形式に変換"""
    return {
      "score": self.score,
      "user_id": self.user_id,
      "recipe_id": self.recipe_id,
      "created_at": self.created_at.isoformat()
    }

  @classmethod
  def from_dict(cls, data: dict) -> "Rating":
    """辞書から生成"""
    return cls(
      score=data["score"],
      user_id=data["user_id"],
      recipe_id=data["recipe_id"],
      created_at=datetime.fromisoformat(data["created_at"])
    )


@dataclass
class Review:
  """レビューモデル"""

  id: str = field(default_factory=lambda: str(uuid4()))
  recipe_id: str = ""
  user_id: str = ""
  rating: int = 5  # 1-5
  comment: str = ""
  helpful_count: int = 0
  helpful_users: list[str] = field(default_factory=list)
  created_at: datetime = field(default_factory=datetime.now)
  updated_at: Optional[datetime] = None

  def to_dict(self) -> dict:
    """辞書形式に変換"""
    return {
      "id": self.id,
      "recipe_id": self.recipe_id,
      "user_id": self.user_id,
      "rating": self.rating,
      "comment": self.comment,
      "helpful_count": self.helpful_count,
      "helpful_users": self.helpful_users,
      "created_at": self.created_at.isoformat(),
      "updated_at": self.updated_at.isoformat() if self.updated_at else None
    }

  @classmethod
  def from_dict(cls, data: dict) -> "Review":
    """辞書から生成"""
    return cls(
      id=data["id"],
      recipe_id=data["recipe_id"],
      user_id=data["user_id"],
      rating=data["rating"],
      comment=data["comment"],
      helpful_count=data.get("helpful_count", 0),
      helpful_users=data.get("helpful_users", []),
      created_at=datetime.fromisoformat(data["created_at"]),
      updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
    )


@dataclass
class RecipeRatingSummary:
  """レシピの評価サマリー"""

  recipe_id: str
  average_rating: float  # 平均評価（小数第1位まで）
  total_reviews: int
  rating_distribution: dict[int, int]  # 各評価の件数 {1: 0, 2: 1, 3: 5, 4: 10, 5: 20}

  def to_dict(self) -> dict:
    """辞書形式に変換"""
    return {
      "recipe_id": self.recipe_id,
      "average_rating": round(self.average_rating, 1),
      "total_reviews": self.total_reviews,
      "rating_distribution": self.rating_distribution
    }
