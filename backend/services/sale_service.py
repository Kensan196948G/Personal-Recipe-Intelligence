"""
特売情報サービス

スーパーのチラシ情報を管理し、価格比較やレシピ推薦を行う。
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class SaleCategory(str, Enum):
    """特売商品カテゴリ"""

    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    MEAT = "meat"
    FISH = "fish"
    DAIRY = "dairy"
    GRAIN = "grain"
    SEASONING = "seasoning"
    OTHER = "other"


@dataclass
class SaleItem:
    """特売商品データモデル"""

    id: str
    store_name: str
    product_name: str
    price: float
    original_price: Optional[float] = None
    unit: str = "個"
    category: SaleCategory = SaleCategory.OTHER
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: datetime = field(
        default_factory=lambda: datetime.now() + timedelta(days=3)
    )
    discount_rate: Optional[float] = None
    image_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """割引率を自動計算"""
        if self.original_price and self.original_price > 0:
            self.discount_rate = round(
                ((self.original_price - self.price) / self.original_price) * 100, 1
            )

    def is_valid(self) -> bool:
        """有効期限チェック"""
        now = datetime.now()
        return self.valid_from <= now <= self.valid_until

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "store_name": self.store_name,
            "product_name": self.product_name,
            "price": self.price,
            "original_price": self.original_price,
            "unit": self.unit,
            "category": self.category.value,
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat(),
            "discount_rate": self.discount_rate,
            "image_url": self.image_url,
            "metadata": self.metadata,
        }


class SaleService:
    """特売情報サービス"""

    def __init__(self):
        self.sale_items: List[SaleItem] = []
        self._ingredient_mapping = self._load_ingredient_mapping()

    def _load_ingredient_mapping(self) -> Dict[str, List[str]]:
        """
        商品名→レシピ材料名のマッピング辞書

        Returns:
          商品名パターンと材料名の対応辞書
        """
        return {
            "たまねぎ": ["玉ねぎ", "たまねぎ", "玉葱", "タマネギ"],
            "にんじん": ["人参", "にんじん", "ニンジン"],
            "じゃがいも": ["じゃがいも", "ジャガイモ", "馬鈴薯"],
            "豚肉": ["豚肉", "豚バラ", "豚ロース", "豚こま"],
            "鶏肉": ["鶏肉", "鶏もも", "鶏むね", "鶏ささみ"],
            "牛肉": ["牛肉", "牛バラ", "牛ロース", "牛こま"],
            "キャベツ": ["キャベツ", "きゃべつ"],
            "トマト": ["トマト", "とまと", "完熟トマト"],
            "牛乳": ["牛乳", "ミルク"],
            "卵": ["卵", "たまご", "玉子"],
        }

    def add_sale_item(self, item: SaleItem) -> None:
        """
        特売商品を追加

        Args:
          item: 特売商品データ
        """
        self.sale_items.append(item)

    def get_active_sales(
        self,
        store_name: Optional[str] = None,
        category: Optional[SaleCategory] = None,
        min_discount: Optional[float] = None,
    ) -> List[SaleItem]:
        """
        有効な特売情報を取得

        Args:
          store_name: 店舗名でフィルタ
          category: カテゴリでフィルタ
          min_discount: 最小割引率（%）

        Returns:
          フィルタされた特売商品リスト
        """
        filtered = [item for item in self.sale_items if item.is_valid()]

        if store_name:
            filtered = [item for item in filtered if item.store_name == store_name]

        if category:
            filtered = [item for item in filtered if item.category == category]

        if min_discount is not None:
            filtered = [
                item
                for item in filtered
                if item.discount_rate and item.discount_rate >= min_discount
            ]

        return sorted(filtered, key=lambda x: x.discount_rate or 0, reverse=True)

    def compare_prices(self, product_name: str) -> List[Dict[str, Any]]:
        """
        商品の価格比較

        Args:
          product_name: 商品名（部分一致）

        Returns:
          価格比較結果（安い順）
        """
        matching_items = [
            item
            for item in self.sale_items
            if product_name.lower() in item.product_name.lower() and item.is_valid()
        ]

        comparison = []
        for item in matching_items:
            comparison.append(
                {
                    "store_name": item.store_name,
                    "product_name": item.product_name,
                    "price": item.price,
                    "unit": item.unit,
                    "discount_rate": item.discount_rate,
                    "valid_until": item.valid_until.isoformat(),
                }
            )

        return sorted(comparison, key=lambda x: x["price"])

    def normalize_ingredient_name(self, product_name: str) -> Optional[str]:
        """
        商品名を正規化してレシピ材料名に変換

        Args:
          product_name: 商品名

        Returns:
          正規化された材料名
        """
        product_lower = product_name.lower()

        for normalized, patterns in self._ingredient_mapping.items():
            for pattern in patterns:
                if pattern.lower() in product_lower:
                    return normalized

        return None

    def get_ingredient_recommendations(
        self, available_ingredients: List[str]
    ) -> List[SaleItem]:
        """
        利用可能な材料から特売おすすめを取得

        Args:
          available_ingredients: レシピで使用する材料リスト

        Returns:
          おすすめ特売商品リスト
        """
        recommendations = []

        for item in self.get_active_sales():
            normalized = self.normalize_ingredient_name(item.product_name)
            if normalized and normalized in available_ingredients:
                recommendations.append(item)

        return sorted(recommendations, key=lambda x: x.discount_rate or 0, reverse=True)

    def get_recipe_cost_estimate(self, ingredients: List[str]) -> Dict[str, Any]:
        """
        レシピの材料費見積もり

        Args:
          ingredients: 材料リスト

        Returns:
          材料費見積もり情報
        """
        total_cost = 0.0
        item_details = []
        available_count = 0

        for ingredient in ingredients:
            # 特売商品から最安値を検索
            matching_sales = [
                item
                for item in self.get_active_sales()
                if self.normalize_ingredient_name(item.product_name) == ingredient
            ]

            if matching_sales:
                cheapest = min(matching_sales, key=lambda x: x.price)
                total_cost += cheapest.price
                available_count += 1
                item_details.append(
                    {
                        "ingredient": ingredient,
                        "product": cheapest.product_name,
                        "price": cheapest.price,
                        "store": cheapest.store_name,
                        "on_sale": True,
                    }
                )
            else:
                item_details.append(
                    {
                        "ingredient": ingredient,
                        "product": None,
                        "price": None,
                        "store": None,
                        "on_sale": False,
                    }
                )

        return {
            "total_cost": round(total_cost, 2),
            "ingredients_count": len(ingredients),
            "available_on_sale": available_count,
            "coverage_rate": (
                round((available_count / len(ingredients)) * 100, 1)
                if ingredients
                else 0
            ),
            "items": item_details,
        }

    def clear_expired_sales(self) -> int:
        """
        期限切れ特売情報を削除

        Returns:
          削除した件数
        """
        original_count = len(self.sale_items)
        self.sale_items = [item for item in self.sale_items if item.is_valid()]
        return original_count - len(self.sale_items)

    def get_statistics(self) -> Dict[str, Any]:
        """
        特売情報統計を取得

        Returns:
          統計情報
        """
        active_sales = self.get_active_sales()

        category_counts = {}
        for item in active_sales:
            category_counts[item.category.value] = (
                category_counts.get(item.category.value, 0) + 1
            )

        store_counts = {}
        for item in active_sales:
            store_counts[item.store_name] = store_counts.get(item.store_name, 0) + 1

        avg_discount = (
            sum(item.discount_rate or 0 for item in active_sales) / len(active_sales)
            if active_sales
            else 0
        )

        return {
            "total_active_sales": len(active_sales),
            "total_all_sales": len(self.sale_items),
            "average_discount_rate": round(avg_discount, 1),
            "categories": category_counts,
            "stores": store_counts,
        }
