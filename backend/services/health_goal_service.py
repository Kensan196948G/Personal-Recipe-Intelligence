"""
Health Goal Service - 健康目標管理サービス

Harris-Benedict式によるBMR計算と日本人の食事摂取基準に基づく推奨値計算を実装。
"""

import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum


class Gender(str, Enum):
  """性別"""
  MALE = "male"
  FEMALE = "female"


class ActivityLevel(str, Enum):
  """活動レベル"""
  LOW = "low"  # 座り仕事中心
  MODERATE = "moderate"  # 軽い運動・立ち仕事
  HIGH = "high"  # 定期的な運動
  ATHLETE = "athlete"  # アスリート


class HealthGoalService:
  """健康目標サービス"""

  # 活動レベル係数（Harris-Benedict式用）
  ACTIVITY_MULTIPLIERS = {
    ActivityLevel.LOW: 1.2,
    ActivityLevel.MODERATE: 1.375,
    ActivityLevel.HIGH: 1.55,
    ActivityLevel.ATHLETE: 1.725,
  }

  # PFCバランス（デフォルト）
  DEFAULT_PFC_RATIO = {
    "protein": 0.15,  # タンパク質 15%
    "fat": 0.25,  # 脂質 25%
    "carbohydrate": 0.60,  # 炭水化物 60%
  }

  def __init__(self, data_dir: str = "data"):
    """
    初期化

    Args:
      data_dir: データ保存ディレクトリ
    """
    self.data_dir = Path(data_dir)
    self.data_dir.mkdir(parents=True, exist_ok=True)
    self.profile_file = self.data_dir / "health_profile.json"
    self.targets_file = self.data_dir / "health_targets.json"
    self.history_file = self.data_dir / "health_history.json"

  def set_profile(
    self,
    age: int,
    gender: Gender,
    weight: float,
    height: float,
    activity_level: ActivityLevel,
  ) -> Dict:
    """
    個人プロファイルを設定

    Args:
      age: 年齢
      gender: 性別
      weight: 体重（kg）
      height: 身長（cm）
      activity_level: 活動レベル

    Returns:
      設定されたプロファイル
    """
    profile = {
      "age": age,
      "gender": gender.value,
      "weight": weight,
      "height": height,
      "activity_level": activity_level.value,
      "updated_at": datetime.now().isoformat(),
    }

    with open(self.profile_file, "w", encoding="utf-8") as f:
      json.dump(profile, f, ensure_ascii=False, indent=2)

    return profile

  def get_profile(self) -> Optional[Dict]:
    """
    プロファイルを取得

    Returns:
      プロファイル（存在しない場合はNone）
    """
    if not self.profile_file.exists():
      return None

    with open(self.profile_file, "r", encoding="utf-8") as f:
      return json.load(f)

  def calculate_bmr(self, age: int, gender: Gender, weight: float, height: float) -> float:
    """
    Harris-Benedict式でBMR（基礎代謝率）を計算

    Args:
      age: 年齢
      gender: 性別
      weight: 体重（kg）
      height: 身長（cm）

    Returns:
      BMR（kcal/日）
    """
    if gender == Gender.MALE:
      # 男性: 66.47 + (13.75 × 体重kg) + (5.00 × 身長cm) - (6.76 × 年齢)
      bmr = 66.47 + (13.75 * weight) + (5.00 * height) - (6.76 * age)
    else:
      # 女性: 655.1 + (9.56 × 体重kg) + (1.85 × 身長cm) - (4.68 × 年齢)
      bmr = 655.1 + (9.56 * weight) + (1.85 * height) - (4.68 * age)

    return round(bmr, 1)

  def calculate_tdee(
    self, age: int, gender: Gender, weight: float, height: float, activity_level: ActivityLevel
  ) -> float:
    """
    TDEE（総消費エネルギー）を計算

    Args:
      age: 年齢
      gender: 性別
      weight: 体重（kg）
      height: 身長（cm）
      activity_level: 活動レベル

    Returns:
      TDEE（kcal/日）
    """
    bmr = self.calculate_bmr(age, gender, weight, height)
    multiplier = self.ACTIVITY_MULTIPLIERS[activity_level]
    tdee = bmr * multiplier
    return round(tdee, 1)

  def get_recommendations(self, profile: Optional[Dict] = None) -> Dict:
    """
    推奨栄養素摂取量を計算

    Args:
      profile: プロファイル（Noneの場合は保存済みプロファイルを使用）

    Returns:
      推奨値
    """
    if profile is None:
      profile = self.get_profile()

    if not profile:
      raise ValueError("プロファイルが設定されていません")

    age = profile["age"]
    gender = Gender(profile["gender"])
    weight = profile["weight"]
    height = profile["height"]
    activity_level = ActivityLevel(profile["activity_level"])

    # TDEE計算
    tdee = self.calculate_tdee(age, gender, weight, height, activity_level)

    # PFCバランスから各栄養素を計算
    protein_kcal = tdee * self.DEFAULT_PFC_RATIO["protein"]
    fat_kcal = tdee * self.DEFAULT_PFC_RATIO["fat"]
    carb_kcal = tdee * self.DEFAULT_PFC_RATIO["carbohydrate"]

    # g換算（タンパク質: 4kcal/g, 脂質: 9kcal/g, 炭水化物: 4kcal/g）
    protein_g = protein_kcal / 4
    fat_g = fat_kcal / 9
    carb_g = carb_kcal / 4

    # 食物繊維（日本人の食事摂取基準: 成人男性21g以上、女性18g以上）
    fiber_g = 21.0 if gender == Gender.MALE else 18.0

    # 塩分（日本人の食事摂取基準: 成人男性7.5g未満、女性6.5g未満）
    salt_g = 7.5 if gender == Gender.MALE else 6.5

    return {
      "calories": round(tdee, 1),
      "protein": round(protein_g, 1),
      "fat": round(fat_g, 1),
      "carbohydrate": round(carb_g, 1),
      "fiber": round(fiber_g, 1),
      "salt": round(salt_g, 1),
    }

  def set_targets(self, targets: Dict) -> Dict:
    """
    目標値を設定

    Args:
      targets: 目標値（calories, protein, fat, carbohydrate, fiber, salt）

    Returns:
      設定された目標値
    """
    target_data = {
      "targets": targets,
      "updated_at": datetime.now().isoformat(),
    }

    with open(self.targets_file, "w", encoding="utf-8") as f:
      json.dump(target_data, f, ensure_ascii=False, indent=2)

    return target_data

  def get_targets(self) -> Optional[Dict]:
    """
    目標値を取得

    Returns:
      目標値（存在しない場合はNone）
    """
    if not self.targets_file.exists():
      return None

    with open(self.targets_file, "r", encoding="utf-8") as f:
      data = json.load(f)
      return data.get("targets")

  def calculate_progress(
    self, nutrition_data: Dict, target_date: Optional[date] = None
  ) -> Dict:
    """
    達成率を計算

    Args:
      nutrition_data: 実際の摂取栄養データ
      target_date: 対象日（Noneの場合は今日）

    Returns:
      達成率データ
    """
    targets = self.get_targets()
    if not targets:
      raise ValueError("目標値が設定されていません")

    if target_date is None:
      target_date = date.today()

    progress = {}
    for nutrient, target_value in targets.items():
      actual_value = nutrition_data.get(nutrient, 0)
      if target_value > 0:
        # 塩分は少ないほど良い（達成率を逆算）
        if nutrient == "salt":
          achievement = max(0, (1 - (actual_value / target_value)) * 100)
        else:
          achievement = (actual_value / target_value) * 100
      else:
        achievement = 0

      progress[nutrient] = {
        "target": target_value,
        "actual": actual_value,
        "achievement": round(min(achievement, 150), 1),  # 上限150%
        "status": self._get_status(achievement, nutrient),
      }

    # 履歴に記録
    self._save_history(target_date, progress)

    return {
      "date": target_date.isoformat(),
      "progress": progress,
    }

  def _get_status(self, achievement: float, nutrient: str) -> str:
    """
    達成度合いのステータスを取得

    Args:
      achievement: 達成率（%）
      nutrient: 栄養素名

    Returns:
      ステータス（excellent, good, fair, poor）
    """
    # 塩分は特殊（少ないほど良い）
    if nutrient == "salt":
      if achievement >= 80:
        return "excellent"
      elif achievement >= 60:
        return "good"
      elif achievement >= 40:
        return "fair"
      else:
        return "poor"

    # 通常の栄養素
    if achievement >= 90:
      return "excellent"
    elif achievement >= 70:
      return "good"
    elif achievement >= 50:
      return "fair"
    else:
      return "poor"

  def _save_history(self, target_date: date, progress: Dict) -> None:
    """
    履歴を保存

    Args:
      target_date: 対象日
      progress: 達成率データ
    """
    history = {}
    if self.history_file.exists():
      with open(self.history_file, "r", encoding="utf-8") as f:
        history = json.load(f)

    date_key = target_date.isoformat()
    history[date_key] = {
      "progress": progress,
      "recorded_at": datetime.now().isoformat(),
    }

    with open(self.history_file, "w", encoding="utf-8") as f:
      json.dump(history, f, ensure_ascii=False, indent=2)

  def get_history(self, days: int = 7) -> List[Dict]:
    """
    履歴を取得

    Args:
      days: 取得する日数

    Returns:
      履歴データ
    """
    history = {}
    if self.history_file.exists():
      with open(self.history_file, "r", encoding="utf-8") as f:
        history = json.load(f)

    # 指定日数分を取得
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    result = []
    current_date = start_date
    while current_date <= end_date:
      date_key = current_date.isoformat()
      if date_key in history:
        result.append({
          "date": date_key,
          "progress": history[date_key]["progress"],
        })
      else:
        result.append({
          "date": date_key,
          "progress": None,
        })
      current_date += timedelta(days=1)

    return result

  def get_advice(self, progress: Dict) -> List[Dict]:
    """
    改善アドバイスを生成

    Args:
      progress: 達成率データ

    Returns:
      アドバイスリスト
    """
    advice_list = []

    for nutrient, data in progress.get("progress", {}).items():
      status = data["status"]
      achievement = data["achievement"]
      target = data["target"]
      actual = data["actual"]

      if status in ["poor", "fair"]:
        advice = self._generate_advice(nutrient, achievement, target, actual)
        if advice:
          advice_list.append({
            "nutrient": nutrient,
            "status": status,
            "achievement": achievement,
            "advice": advice,
          })

    return advice_list

  def _generate_advice(
    self, nutrient: str, achievement: float, target: float, actual: float
  ) -> str:
    """
    栄養素別のアドバイスを生成

    Args:
      nutrient: 栄養素名
      achievement: 達成率
      target: 目標値
      actual: 実際の値

    Returns:
      アドバイス文
    """
    diff = target - actual

    advice_map = {
      "calories": f"カロリーが目標より{abs(diff):.0f}kcal {'不足' if diff > 0 else '過剰'}しています。"
      f"{'主食や主菜を少し増やしましょう。' if diff > 0 else '間食や脂質の多い食品を控えめにしましょう。'}",
      "protein": f"タンパク質が目標より{abs(diff):.1f}g不足しています。"
      f"肉・魚・卵・大豆製品を積極的に摂取しましょう。",
      "fat": f"脂質が目標より{abs(diff):.1f}g {'不足' if diff > 0 else '過剰'}しています。"
      f"{'ナッツや魚を取り入れましょう。' if diff > 0 else '揚げ物や脂身の多い肉を控えましょう。'}",
      "carbohydrate": f"炭水化物が目標より{abs(diff):.1f}g {'不足' if diff > 0 else '過剰'}しています。"
      f"{'ご飯やパンなどの主食を適量摂取しましょう。' if diff > 0 else '主食の量を見直しましょう。'}",
      "fiber": f"食物繊維が目標より{abs(diff):.1f}g不足しています。"
      f"野菜・きのこ・海藻・全粒穀物を増やしましょう。",
      "salt": f"塩分が目標より{abs(diff):.1f}g過剰です。"
      f"減塩調味料の使用や、出汁を活かした調理を心がけましょう。",
    }

    return advice_map.get(nutrient, "")
