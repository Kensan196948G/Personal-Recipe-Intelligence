"""
チラシパーサー

スーパーのチラシ画像から特売情報を抽出する。
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid

from .sale_service import SaleItem, SaleCategory


@dataclass
class ParsedProduct:
    """パース済み商品データ"""

    product_name: str
    price: float
    unit: str = "個"
    original_price: Optional[float] = None
    category: SaleCategory = SaleCategory.OTHER
    confidence: float = 1.0


class FlyerParser:
    """チラシパーサー"""

    def __init__(self):
        self.category_keywords = self._load_category_keywords()
        self.price_patterns = self._compile_price_patterns()

    def _load_category_keywords(self) -> Dict[SaleCategory, List[str]]:
        """
        カテゴリ分類キーワード辞書

        Returns:
          カテゴリとキーワードの対応辞書
        """
        return {
            SaleCategory.VEGETABLE: [
                "野菜",
                "やさい",
                "玉ねぎ",
                "たまねぎ",
                "人参",
                "にんじん",
                "じゃがいも",
                "キャベツ",
                "レタス",
                "白菜",
                "ほうれん草",
                "ネギ",
                "ねぎ",
                "大根",
                "なす",
                "ピーマン",
                "トマト",
                "きゅうり",
            ],
            SaleCategory.FRUIT: [
                "果物",
                "くだもの",
                "りんご",
                "リンゴ",
                "みかん",
                "バナナ",
                "いちご",
                "イチゴ",
                "メロン",
                "ぶどう",
                "桃",
                "梨",
            ],
            SaleCategory.MEAT: [
                "肉",
                "豚",
                "牛",
                "鶏",
                "ひき肉",
                "バラ",
                "ロース",
                "もも",
                "むね",
                "ささみ",
                "こま",
            ],
            SaleCategory.FISH: [
                "魚",
                "さかな",
                "鮭",
                "サーモン",
                "マグロ",
                "まぐろ",
                "サバ",
                "さば",
                "アジ",
                "あじ",
                "イワシ",
                "いわし",
                "刺身",
            ],
            SaleCategory.DAIRY: [
                "乳製品",
                "牛乳",
                "ミルク",
                "ヨーグルト",
                "チーズ",
                "バター",
                "卵",
                "たまご",
                "玉子",
            ],
            SaleCategory.GRAIN: [
                "米",
                "こめ",
                "パン",
                "麺",
                "めん",
                "うどん",
                "そば",
                "パスタ",
                "小麦粉",
            ],
            SaleCategory.SEASONING: [
                "調味料",
                "醤油",
                "しょうゆ",
                "味噌",
                "みそ",
                "塩",
                "砂糖",
                "酢",
                "油",
                "みりん",
                "料理酒",
            ],
        }

    def _compile_price_patterns(self) -> List[re.Pattern]:
        """
        価格抽出用正規表現パターン

        Returns:
          正規表現パターンリスト
        """
        return [
            re.compile(r"(\d+)円"),
            re.compile(r"¥\s*(\d+)"),
            re.compile(r"(\d+)\s*円"),
            re.compile(r"(\d{2,4})(?=\s|$)"),  # 数字のみ（2-4桁）
        ]

    def classify_category(self, product_name: str) -> SaleCategory:
        """
        商品名からカテゴリを分類

        Args:
          product_name: 商品名

        Returns:
          分類されたカテゴリ
        """
        product_lower = product_name.lower()

        # 特定のキーワードを優先的にチェック（より具体的なもの）
        # 例: 「牛乳」は「乳製品」、「牛」より先にマッチさせる
        priority_matches = [
            ("牛乳", SaleCategory.DAIRY),
            ("ミルク", SaleCategory.DAIRY),
            ("ヨーグルト", SaleCategory.DAIRY),
            ("チーズ", SaleCategory.DAIRY),
        ]

        for keyword, category in priority_matches:
            if keyword.lower() in product_lower:
                return category

        # 通常のカテゴリマッチング
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in product_lower:
                    return category

        return SaleCategory.OTHER

    def extract_price(self, text: str) -> Optional[float]:
        """
        テキストから価格を抽出

        Args:
          text: OCR結果テキスト

        Returns:
          抽出された価格（見つからない場合はNone）
        """
        for pattern in self.price_patterns:
            match = pattern.search(text)
            if match:
                try:
                    price = float(match.group(1))
                    # 妥当な価格範囲チェック（10円〜100,000円）
                    if 10 <= price <= 100000:
                        return price
                except (ValueError, IndexError):
                    continue

        return None

    def extract_unit(self, text: str) -> str:
        """
        単位を抽出

        Args:
          text: OCR結果テキスト

        Returns:
          単位（デフォルト: "個"）
        """
        units = ["個", "本", "袋", "パック", "kg", "g", "L", "ml", "枚"]

        text_lower = text.lower()
        for unit in units:
            if unit in text or unit.lower() in text_lower:
                return unit

        # 数量表現の検出
        if re.search(r"\d+\s*個入", text):
            return "袋"
        if re.search(r"\d+\s*g", text):
            return "g"
        if re.search(r"\d+\s*kg", text):
            return "kg"

        return "個"

    def parse_ocr_result(
        self, ocr_text: str, store_name: str = "不明"
    ) -> List[ParsedProduct]:
        """
        OCR結果から商品情報を抽出

        Args:
          ocr_text: OCR結果テキスト
          store_name: 店舗名

        Returns:
          パース済み商品リスト
        """
        products = []

        # 行ごとに分割
        lines = ocr_text.split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # 価格を抽出
            price = self.extract_price(line)
            if not price:
                continue

            # 商品名を推定（価格より前のテキスト）
            product_name = re.sub(r"[\d円¥]+", "", line).strip()
            if not product_name or len(product_name) < 2:
                # 前の行から商品名を取得
                if i > 0:
                    product_name = lines[i - 1].strip()

            if not product_name or len(product_name) < 2:
                continue

            # カテゴリ分類
            category = self.classify_category(product_name)

            # 単位抽出
            unit = self.extract_unit(line)

            products.append(
                ParsedProduct(
                    product_name=product_name,
                    price=price,
                    unit=unit,
                    category=category,
                    confidence=0.8,
                )
            )

        return products

    def parse_structured_data(
        self, data: Dict[str, Any], store_name: str = "不明"
    ) -> List[ParsedProduct]:
        """
        構造化データから商品情報を抽出

        Args:
          data: 構造化された商品データ（例: {'items': [{'name': '...', 'price': ...}]}）
          store_name: 店舗名

        Returns:
          パース済み商品リスト
        """
        products = []

        items = data.get("items", [])
        for item in items:
            product_name = item.get("name") or item.get("product_name")
            price = item.get("price")

            if not product_name or not price:
                continue

            category_str = item.get("category")
            category = (
                SaleCategory[category_str.upper()]
                if category_str
                else self.classify_category(product_name)
            )

            products.append(
                ParsedProduct(
                    product_name=product_name,
                    price=float(price),
                    unit=item.get("unit", "個"),
                    original_price=item.get("original_price"),
                    category=category,
                    confidence=1.0,
                )
            )

        return products

    def create_sale_items(
        self,
        parsed_products: List[ParsedProduct],
        store_name: str,
        valid_days: int = 3,
    ) -> List[SaleItem]:
        """
        パース済み商品からSaleItemを生成

        Args:
          parsed_products: パース済み商品リスト
          store_name: 店舗名
          valid_days: 有効日数

        Returns:
          特売商品リスト
        """
        sale_items = []
        now = datetime.now()

        for product in parsed_products:
            sale_item = SaleItem(
                id=str(uuid.uuid4()),
                store_name=store_name,
                product_name=product.product_name,
                price=product.price,
                original_price=product.original_price,
                unit=product.unit,
                category=product.category,
                valid_from=now,
                valid_until=now + timedelta(days=valid_days),
                metadata={"confidence": product.confidence},
            )
            sale_items.append(sale_item)

        return sale_items

    def extract_store_name(self, ocr_text: str) -> str:
        """
        OCR結果から店舗名を抽出

        Args:
          ocr_text: OCR結果テキスト

        Returns:
          店舗名（見つからない場合は"不明"）
        """
        # 日本の主要スーパー名リスト
        known_stores = [
            "イオン",
            "AEON",
            "西友",
            "SEIYU",
            "イトーヨーカドー",
            "ヨーカドー",
            "ライフ",
            "LIFE",
            "マルエツ",
            "Olympic",
            "オリンピック",
            "サミット",
            "SUMMIT",
            "ダイエー",
            "マックスバリュ",
            "業務スーパー",
        ]

        ocr_upper = ocr_text.upper()
        for store in known_stores:
            if store.upper() in ocr_upper or store in ocr_text:
                return store

        # 最初の行から店舗名を推定（大文字が多い場合）
        first_line = ocr_text.split("\n")[0].strip()
        if len(first_line) > 2 and len(first_line) < 20:
            return first_line

        return "不明"

    def validate_parsed_products(
        self, products: List[ParsedProduct], min_confidence: float = 0.5
    ) -> List[ParsedProduct]:
        """
        パース済み商品の検証とフィルタリング

        Args:
          products: パース済み商品リスト
          min_confidence: 最小信頼度

        Returns:
          検証済み商品リスト
        """
        validated = []

        for product in products:
            # 信頼度チェック
            if product.confidence < min_confidence:
                continue

            # 商品名の長さチェック
            if len(product.product_name) < 2 or len(product.product_name) > 50:
                continue

            # 価格の妥当性チェック
            if product.price <= 0 or product.price > 100000:
                continue

            validated.append(product)

        return validated
