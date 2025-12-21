"""
食事バランス解析サービス

PFCバランス計算、栄養バランス評価、スコア算出を提供
"""

from typing import Dict, List, Any


# 日本人の食事摂取基準（成人の平均的な目安）
DAILY_REFERENCE = {
    "calories": 2000,
    "protein": 60,  # g
    "fat": 55,  # g
    "carbs": 300,  # g
    "fiber": 20,  # g
    "salt": 7.5,  # g
}

# PFC理想比率（カロリーベース）
PFC_IDEAL_RATIO = {"protein": 0.15, "fat": 0.25, "carbs": 0.60}  # 15%  # 25%  # 60%

# カロリー換算係数（g あたり）
CALORIE_FACTOR = {
    "protein": 4,  # タンパク質 4kcal/g
    "fat": 9,  # 脂質 9kcal/g
    "carbs": 4,  # 炭水化物 4kcal/g
}


class BalanceService:
    """食事バランス解析サービス"""

    @staticmethod
    def calculate_pfc_balance(nutrition: Dict[str, float]) -> Dict[str, Any]:
        """
        PFCバランスを計算

        Args:
          nutrition: 栄養素データ（protein, fat, carbs を含む）

        Returns:
          PFCバランス情報（比率、カロリー、評価）
        """
        protein = nutrition.get("protein", 0)
        fat = nutrition.get("fat", 0)
        carbs = nutrition.get("carbs", 0)

        # 各栄養素のカロリー計算
        protein_cal = protein * CALORIE_FACTOR["protein"]
        fat_cal = fat * CALORIE_FACTOR["fat"]
        carbs_cal = carbs * CALORIE_FACTOR["carbs"]
        total_cal = protein_cal + fat_cal + carbs_cal

        # 比率計算（ゼロ除算回避）
        if total_cal == 0:
            return {
                "protein_ratio": 0,
                "fat_ratio": 0,
                "carbs_ratio": 0,
                "protein_cal": 0,
                "fat_cal": 0,
                "carbs_cal": 0,
                "total_cal": 0,
                "balance_score": 0,
                "is_balanced": False,
                "recommendations": ["栄養データが不足しています"],
            }

        protein_ratio = protein_cal / total_cal
        fat_ratio = fat_cal / total_cal
        carbs_ratio = carbs_cal / total_cal

        # 理想比率との差異計算
        protein_diff = abs(protein_ratio - PFC_IDEAL_RATIO["protein"])
        fat_diff = abs(fat_ratio - PFC_IDEAL_RATIO["fat"])
        carbs_diff = abs(carbs_ratio - PFC_IDEAL_RATIO["carbs"])

        # バランススコア（100点満点、差異が小さいほど高得点）
        total_diff = protein_diff + fat_diff + carbs_diff
        balance_score = max(0, 100 - (total_diff * 200))

        # 評価とアドバイス
        is_balanced = balance_score >= 70
        recommendations = BalanceService._generate_pfc_recommendations(
            protein_ratio, fat_ratio, carbs_ratio
        )

        return {
            "protein_ratio": round(protein_ratio, 3),
            "fat_ratio": round(fat_ratio, 3),
            "carbs_ratio": round(carbs_ratio, 3),
            "protein_cal": round(protein_cal, 1),
            "fat_cal": round(fat_cal, 1),
            "carbs_cal": round(carbs_cal, 1),
            "total_cal": round(total_cal, 1),
            "balance_score": round(balance_score, 1),
            "is_balanced": is_balanced,
            "recommendations": recommendations,
            # グラフ用データ
            "pie_chart_data": [
                {
                    "name": "タンパク質",
                    "value": round(protein_ratio * 100, 1),
                    "calories": round(protein_cal, 1),
                },
                {
                    "name": "脂質",
                    "value": round(fat_ratio * 100, 1),
                    "calories": round(fat_cal, 1),
                },
                {
                    "name": "炭水化物",
                    "value": round(carbs_ratio * 100, 1),
                    "calories": round(carbs_cal, 1),
                },
            ],
        }

    @staticmethod
    def _generate_pfc_recommendations(
        protein_ratio: float, fat_ratio: float, carbs_ratio: float
    ) -> List[str]:
        """PFC比率に基づくアドバイス生成"""
        recommendations = []

        # タンパク質評価
        if protein_ratio < PFC_IDEAL_RATIO["protein"] - 0.05:
            recommendations.append(
                "タンパク質が不足気味です。肉・魚・大豆製品を追加しましょう"
            )
        elif protein_ratio > PFC_IDEAL_RATIO["protein"] + 0.05:
            recommendations.append("タンパク質がやや多めです")

        # 脂質評価
        if fat_ratio < PFC_IDEAL_RATIO["fat"] - 0.05:
            recommendations.append("脂質が不足しています。良質な油を適量摂りましょう")
        elif fat_ratio > PFC_IDEAL_RATIO["fat"] + 0.1:
            recommendations.append("脂質が多めです。揚げ物や油の使用を控えめに")

        # 炭水化物評価
        if carbs_ratio < PFC_IDEAL_RATIO["carbs"] - 0.1:
            recommendations.append(
                "炭水化物が不足しています。ご飯やパンを追加しましょう"
            )
        elif carbs_ratio > PFC_IDEAL_RATIO["carbs"] + 0.1:
            recommendations.append("炭水化物が多めです。主食の量を調整しましょう")

        if not recommendations:
            recommendations.append("理想的なPFCバランスです")

        return recommendations

    @staticmethod
    def evaluate_daily_balance(
        recipes_nutrition: List[Dict[str, float]],
    ) -> Dict[str, Any]:
        """
        1日の食事バランスを評価

        Args:
          recipes_nutrition: レシピごとの栄養素データのリスト

        Returns:
          1日のバランス評価
        """
        # 合計値計算
        total = {
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "carbs": 0,
            "fiber": 0,
            "salt": 0,
        }

        for nutrition in recipes_nutrition:
            for key in total.keys():
                total[key] += nutrition.get(key, 0)

        # 充足率計算
        fulfillment = {}
        for key, value in total.items():
            reference = DAILY_REFERENCE[key]
            fulfillment[key] = (
                round((value / reference) * 100, 1) if reference > 0 else 0
            )

        # 総合スコア計算（各栄養素の充足率から）
        overall_score = BalanceService._calculate_overall_score(fulfillment)

        # 評価レベル判定
        evaluation_level = BalanceService._get_evaluation_level(overall_score)

        # アドバイス生成
        recommendations = BalanceService._generate_daily_recommendations(
            fulfillment, total
        )

        # PFCバランス
        pfc_balance = BalanceService.calculate_pfc_balance(total)

        return {
            "total": total,
            "fulfillment": fulfillment,
            "overall_score": round(overall_score, 1),
            "evaluation_level": evaluation_level,
            "pfc_balance": pfc_balance,
            "recommendations": recommendations,
            # グラフ用データ
            "bar_chart_data": [
                {
                    "nutrient": "カロリー",
                    "actual": round(total["calories"], 1),
                    "reference": DAILY_REFERENCE["calories"],
                    "fulfillment": fulfillment["calories"],
                },
                {
                    "nutrient": "タンパク質",
                    "actual": round(total["protein"], 1),
                    "reference": DAILY_REFERENCE["protein"],
                    "fulfillment": fulfillment["protein"],
                },
                {
                    "nutrient": "脂質",
                    "actual": round(total["fat"], 1),
                    "reference": DAILY_REFERENCE["fat"],
                    "fulfillment": fulfillment["fat"],
                },
                {
                    "nutrient": "炭水化物",
                    "actual": round(total["carbs"], 1),
                    "reference": DAILY_REFERENCE["carbs"],
                    "fulfillment": fulfillment["carbs"],
                },
                {
                    "nutrient": "食物繊維",
                    "actual": round(total["fiber"], 1),
                    "reference": DAILY_REFERENCE["fiber"],
                    "fulfillment": fulfillment["fiber"],
                },
                {
                    "nutrient": "塩分",
                    "actual": round(total["salt"], 1),
                    "reference": DAILY_REFERENCE["salt"],
                    "fulfillment": fulfillment["salt"],
                },
            ],
            "radar_chart_data": [
                {"category": "カロリー", "score": min(100, fulfillment["calories"])},
                {"category": "タンパク質", "score": min(100, fulfillment["protein"])},
                {"category": "脂質", "score": min(100, fulfillment["fat"])},
                {"category": "炭水化物", "score": min(100, fulfillment["carbs"])},
                {"category": "食物繊維", "score": min(100, fulfillment["fiber"])},
                {
                    "category": "塩分適正",
                    "score": BalanceService._salt_score(fulfillment["salt"]),
                },
            ],
        }

    @staticmethod
    def _calculate_overall_score(fulfillment: Dict[str, float]) -> float:
        """
        総合バランススコアを計算

        理想は各栄養素が100%に近いこと
        塩分は100%以下が望ましい
        """
        scores = []

        for key, value in fulfillment.items():
            if key == "salt":
                # 塩分は100%以下が理想（超過はマイナス評価）
                if value <= 100:
                    scores.append(100)
                else:
                    scores.append(max(0, 100 - (value - 100)))
            else:
                # その他は80-120%が理想範囲
                if 80 <= value <= 120:
                    scores.append(100)
                elif value < 80:
                    scores.append(value * 1.25)  # 80%で100点
                else:
                    # 120%超は減点
                    over = value - 120
                    scores.append(max(0, 100 - over * 0.5))

        return sum(scores) / len(scores) if scores else 0

    @staticmethod
    def _salt_score(fulfillment: float) -> float:
        """塩分スコア（低いほど良い）"""
        if fulfillment <= 80:
            return 100
        elif fulfillment <= 100:
            return 100 - (fulfillment - 80)
        else:
            return max(0, 80 - (fulfillment - 100) * 0.5)

    @staticmethod
    def _get_evaluation_level(score: float) -> str:
        """スコアから評価レベルを判定"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "fair"
        else:
            return "needs_improvement"

    @staticmethod
    def _generate_daily_recommendations(
        fulfillment: Dict[str, float], total: Dict[str, float]
    ) -> List[str]:
        """1日の食事バランスに基づくアドバイス生成"""
        recommendations = []

        # カロリー
        if fulfillment["calories"] < 80:
            recommendations.append("カロリーが不足しています。食事量を増やしましょう")
        elif fulfillment["calories"] > 120:
            recommendations.append("カロリーオーバーです。食事量を控えめに")

        # タンパク質
        if fulfillment["protein"] < 80:
            recommendations.append(
                "タンパク質が不足しています。肉・魚・卵・大豆製品を増やしましょう"
            )

        # 脂質
        if fulfillment["fat"] > 120:
            recommendations.append("脂質が多めです。揚げ物や油の使用を控えましょう")

        # 炭水化物
        if fulfillment["carbs"] < 80:
            recommendations.append(
                "炭水化物が不足しています。主食をしっかり摂りましょう"
            )
        elif fulfillment["carbs"] > 120:
            recommendations.append("炭水化物が多めです。主食の量を調整しましょう")

        # 食物繊維
        if fulfillment["fiber"] < 80:
            recommendations.append(
                "食物繊維が不足しています。野菜・海藻・きのこを増やしましょう"
            )

        # 塩分
        if fulfillment["salt"] > 100:
            recommendations.append("塩分が多めです。減塩を心がけましょう")

        if not recommendations:
            recommendations.append("バランスの取れた食事です")

        return recommendations

    @staticmethod
    def calculate_nutrition_score(nutrition: Dict[str, float]) -> Dict[str, Any]:
        """
        栄養バランススコアを算出

        Args:
          nutrition: 栄養素データ

        Returns:
          スコア詳細
        """
        # PFCバランススコア
        pfc_balance = BalanceService.calculate_pfc_balance(nutrition)
        pfc_score = pfc_balance["balance_score"]

        # 各栄養素の適正スコア（1食あたりの目安として1日の1/3を基準）
        daily_ref_per_meal = {k: v / 3 for k, v in DAILY_REFERENCE.items()}

        nutrient_scores = {}
        for key, reference in daily_ref_per_meal.items():
            actual = nutrition.get(key, 0)
            if reference > 0:
                ratio = actual / reference
                # 80-120%が理想
                if 0.8 <= ratio <= 1.2:
                    nutrient_scores[key] = 100
                elif ratio < 0.8:
                    nutrient_scores[key] = ratio * 125
                else:
                    nutrient_scores[key] = max(0, 100 - (ratio - 1.2) * 100)
            else:
                nutrient_scores[key] = 0

        # 総合スコア
        avg_nutrient_score = (
            sum(nutrient_scores.values()) / len(nutrient_scores)
            if nutrient_scores
            else 0
        )
        overall_score = pfc_score * 0.4 + avg_nutrient_score * 0.6

        return {
            "overall_score": round(overall_score, 1),
            "pfc_score": round(pfc_score, 1),
            "nutrient_scores": {k: round(v, 1) for k, v in nutrient_scores.items()},
            "evaluation": BalanceService._get_evaluation_level(overall_score),
            "is_healthy": overall_score >= 70,
        }

    @staticmethod
    def get_recipe_balance_evaluation(nutrition: Dict[str, float]) -> Dict[str, Any]:
        """
        レシピ単体のバランス評価

        Args:
          nutrition: 栄養素データ

        Returns:
          バランス評価の完全データ
        """
        pfc_balance = BalanceService.calculate_pfc_balance(nutrition)
        nutrition_score = BalanceService.calculate_nutrition_score(nutrition)

        return {
            "nutrition": nutrition,
            "pfc_balance": pfc_balance,
            "score": nutrition_score,
            "daily_reference_percentage": {
                key: round((nutrition.get(key, 0) / DAILY_REFERENCE[key]) * 100, 1)
                for key in DAILY_REFERENCE.keys()
            },
        }
