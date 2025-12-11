"""
チラシパーサーのテスト

flyer_parser.py の機能を検証する。
"""

import pytest
from datetime import datetime, timedelta
from backend.services.flyer_parser import FlyerParser, ParsedProduct
from backend.services.sale_service import SaleCategory


class TestFlyerParser:
    """FlyerParser のテスト"""

    @pytest.fixture
    def parser(self):
        """テスト用パーサーインスタンス"""
        return FlyerParser()

    def test_classify_category_vegetable(self, parser):
        """野菜カテゴリの分類"""
        assert parser.classify_category("たまねぎ") == SaleCategory.VEGETABLE
        assert parser.classify_category("国産人参") == SaleCategory.VEGETABLE
        assert parser.classify_category("キャベツ 1玉") == SaleCategory.VEGETABLE

    def test_classify_category_meat(self, parser):
        """肉カテゴリの分類"""
        assert parser.classify_category("豚バラ肉") == SaleCategory.MEAT
        assert parser.classify_category("国産牛ロース") == SaleCategory.MEAT
        assert parser.classify_category("鶏もも肉") == SaleCategory.MEAT

    def test_classify_category_fish(self, parser):
        """魚カテゴリの分類"""
        assert parser.classify_category("鮭切り身") == SaleCategory.FISH
        assert parser.classify_category("まぐろ刺身") == SaleCategory.FISH

    def test_classify_category_dairy(self, parser):
        """乳製品カテゴリの分類"""
        assert parser.classify_category("牛乳 1L") == SaleCategory.DAIRY
        assert parser.classify_category("卵 10個入") == SaleCategory.DAIRY
        assert parser.classify_category("ヨーグルト") == SaleCategory.DAIRY

    def test_classify_category_other(self, parser):
        """その他カテゴリ（該当なし）"""
        assert parser.classify_category("不明な商品") == SaleCategory.OTHER

    def test_extract_price_with_yen(self, parser):
        """「円」付き価格の抽出"""
        assert parser.extract_price("たまねぎ 98円") == 98.0
        assert parser.extract_price("牛乳 168 円") == 168.0

    def test_extract_price_with_yen_symbol(self, parser):
        """「¥」記号付き価格の抽出"""
        assert parser.extract_price("¥198") == 198.0
        assert parser.extract_price("¥ 250") == 250.0

    def test_extract_price_number_only(self, parser):
        """数字のみの価格抽出"""
        assert parser.extract_price("298") == 298.0
        assert parser.extract_price("1980") == 1980.0

    def test_extract_price_none(self, parser):
        """価格が見つからない場合"""
        assert parser.extract_price("たまねぎ") is None
        assert parser.extract_price("特売中") is None

    def test_extract_price_invalid_range(self, parser):
        """不正な価格範囲"""
        assert parser.extract_price("5円") is None  # 10円未満
        assert parser.extract_price("200000円") is None  # 100,000円超

    def test_extract_unit_basic(self, parser):
        """基本単位の抽出"""
        assert parser.extract_unit("りんご 5個") == "個"
        assert parser.extract_unit("にんじん 3本") == "本"
        assert parser.extract_unit("牛乳 1L") == "L"

    def test_extract_unit_weight(self, parser):
        """重量単位の抽出"""
        assert parser.extract_unit("豚肉 100g") == "g"
        assert parser.extract_unit("米 5kg") == "kg"

    def test_extract_unit_default(self, parser):
        """デフォルト単位"""
        assert parser.extract_unit("たまねぎ") == "個"

    def test_parse_ocr_result_simple(self, parser):
        """シンプルなOCR結果のパース"""
        ocr_text = """
    たまねぎ
    98円
    にんじん 3本
    158円
    """

        products = parser.parse_ocr_result(ocr_text, "テストスーパー")

        assert len(products) >= 1
        assert any(p.product_name == "たまねぎ" for p in products)

    def test_parse_ocr_result_with_category(self, parser):
        """カテゴリ付きパース"""
        ocr_text = """
    豚バラ肉 100g
    198円
    """

        products = parser.parse_ocr_result(ocr_text, "テストスーパー")

        assert len(products) >= 1
        meat_product = next((p for p in products if "肉" in p.product_name), None)
        if meat_product:
            assert meat_product.category == SaleCategory.MEAT

    def test_parse_structured_data(self, parser):
        """構造化データのパース"""
        data = {
            "items": [
                {
                    "name": "たまねぎ",
                    "price": 98,
                    "unit": "個",
                    "category": "vegetable",
                    "original_price": 150,
                },
                {
                    "name": "牛乳",
                    "price": 168,
                    "unit": "L",
                },
            ]
        }

        products = parser.parse_structured_data(data, "テストスーパー")

        assert len(products) == 2
        assert products[0].product_name == "たまねぎ"
        assert products[0].price == 98.0
        assert products[0].category == SaleCategory.VEGETABLE
        assert products[0].original_price == 150

    def test_create_sale_items(self, parser):
        """SaleItem生成"""
        parsed_products = [
            ParsedProduct(
                product_name="たまねぎ",
                price=98.0,
                unit="個",
                category=SaleCategory.VEGETABLE,
            ),
            ParsedProduct(
                product_name="牛乳",
                price=168.0,
                unit="L",
                category=SaleCategory.DAIRY,
            ),
        ]

        sale_items = parser.create_sale_items(
            parsed_products, "テストスーパー", valid_days=5
        )

        assert len(sale_items) == 2
        assert sale_items[0].store_name == "テストスーパー"
        assert sale_items[0].product_name == "たまねぎ"
        assert sale_items[0].price == 98.0

        # 有効期限チェック
        expected_valid_until = datetime.now() + timedelta(days=5)
        assert (
            abs((sale_items[0].valid_until - expected_valid_until).total_seconds()) < 60
        )

    def test_extract_store_name_known_stores(self, parser):
        """既知店舗名の抽出"""
        assert parser.extract_store_name("イオン 今週の特売") == "イオン"
        assert parser.extract_store_name("AEON SALE") == "AEON"
        assert parser.extract_store_name("西友チラシ") == "西友"

    def test_extract_store_name_from_first_line(self, parser):
        """最初の行から店舗名推定"""
        ocr_text = """マイスーパー
たまねぎ 98円
"""
        assert parser.extract_store_name(ocr_text) == "マイスーパー"

    def test_extract_store_name_unknown(self, parser):
        """不明な店舗名"""
        # 長すぎる行や商品情報のみのテキストは「不明」を返す
        assert (
            parser.extract_store_name("これは長すぎる店舗名の例ですので推定できません")
            == "不明"
        )

    def test_validate_parsed_products(self, parser):
        """パース結果の検証"""
        products = [
            ParsedProduct(
                product_name="たまねぎ",
                price=98.0,
                confidence=0.9,
            ),
            ParsedProduct(
                product_name="X",  # 商品名が短すぎる
                price=100.0,
                confidence=0.8,
            ),
            ParsedProduct(
                product_name="正常な商品",
                price=-50.0,  # 不正な価格
                confidence=0.9,
            ),
            ParsedProduct(
                product_name="低信頼度商品",
                price=100.0,
                confidence=0.3,  # 信頼度が低い
            ),
        ]

        validated = parser.validate_parsed_products(products, min_confidence=0.5)

        assert len(validated) == 1
        assert validated[0].product_name == "たまねぎ"


class TestIntegration:
    """統合テスト"""

    def test_full_parsing_workflow(self):
        """完全なパースワークフロー"""
        parser = FlyerParser()

        # OCRテキスト（実際のチラシを模した形式）
        ocr_text = """
    イオン 今週の大特価

    【野菜】
    国産たまねぎ 98円
    新鮮にんじん 3本 158円
    キャベツ 1玉 128円

    【お肉】
    豚バラ肉 100g 198円
    国産鶏もも肉 100g 88円

    【乳製品】
    牛乳 1L 168円
    """

        # 1. 店舗名抽出
        store_name = parser.extract_store_name(ocr_text)
        assert store_name == "イオン"

        # 2. 商品パース
        products = parser.parse_ocr_result(ocr_text, store_name)

        # 3. 検証
        validated = parser.validate_parsed_products(products)

        # 4. SaleItem生成
        sale_items = parser.create_sale_items(validated, store_name, valid_days=3)

        assert len(sale_items) > 0
        assert all(item.store_name == "イオン" for item in sale_items)
        assert all(item.is_valid() for item in sale_items)
