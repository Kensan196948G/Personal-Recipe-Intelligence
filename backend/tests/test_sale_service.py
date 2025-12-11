"""
特売情報サービスのテスト

sale_service.py の機能を検証する。
"""

import pytest
from datetime import datetime, timedelta
from backend.services.sale_service import (
    SaleService,
    SaleItem,
    SaleCategory,
)


class TestSaleItem:
    """SaleItem データモデルのテスト"""

    def test_sale_item_creation(self):
        """基本的な SaleItem 作成"""
        item = SaleItem(
            id="test-001",
            store_name="テストスーパー",
            product_name="テスト商品",
            price=100.0,
            original_price=150.0,
            category=SaleCategory.VEGETABLE,
        )

        assert item.id == "test-001"
        assert item.store_name == "テストスーパー"
        assert item.product_name == "テスト商品"
        assert item.price == 100.0
        assert item.original_price == 150.0
        assert item.category == SaleCategory.VEGETABLE

    def test_discount_rate_calculation(self):
        """割引率の自動計算"""
        item = SaleItem(
            id="test-002",
            store_name="テストスーパー",
            product_name="たまねぎ",
            price=80.0,
            original_price=100.0,
        )

        assert item.discount_rate == 20.0

    def test_discount_rate_none_when_no_original(self):
        """元値がない場合は割引率なし"""
        item = SaleItem(
            id="test-003",
            store_name="テストスーパー",
            product_name="にんじん",
            price=50.0,
        )

        assert item.discount_rate is None

    def test_is_valid_within_period(self):
        """有効期限内の判定"""
        now = datetime.now()
        item = SaleItem(
            id="test-004",
            store_name="テストスーパー",
            product_name="キャベツ",
            price=100.0,
            valid_from=now - timedelta(days=1),
            valid_until=now + timedelta(days=1),
        )

        assert item.is_valid() is True

    def test_is_valid_expired(self):
        """期限切れの判定"""
        now = datetime.now()
        item = SaleItem(
            id="test-005",
            store_name="テストスーパー",
            product_name="レタス",
            price=100.0,
            valid_from=now - timedelta(days=5),
            valid_until=now - timedelta(days=1),
        )

        assert item.is_valid() is False

    def test_to_dict(self):
        """辞書形式への変換"""
        item = SaleItem(
            id="test-006",
            store_name="テストスーパー",
            product_name="トマト",
            price=200.0,
            category=SaleCategory.VEGETABLE,
        )

        data = item.to_dict()

        assert data["id"] == "test-006"
        assert data["store_name"] == "テストスーパー"
        assert data["product_name"] == "トマト"
        assert data["price"] == 200.0
        assert data["category"] == "vegetable"


class TestSaleService:
    """SaleService のテスト"""

    @pytest.fixture
    def service(self):
        """テスト用 SaleService インスタンス"""
        return SaleService()

    @pytest.fixture
    def sample_items(self):
        """テスト用サンプルデータ"""
        now = datetime.now()
        return [
            SaleItem(
                id="item-001",
                store_name="イオン",
                product_name="たまねぎ",
                price=98.0,
                original_price=150.0,
                category=SaleCategory.VEGETABLE,
                valid_from=now,
                valid_until=now + timedelta(days=3),
            ),
            SaleItem(
                id="item-002",
                store_name="西友",
                product_name="たまねぎ",
                price=120.0,
                original_price=150.0,
                category=SaleCategory.VEGETABLE,
                valid_from=now,
                valid_until=now + timedelta(days=2),
            ),
            SaleItem(
                id="item-003",
                store_name="イオン",
                product_name="豚肉",
                price=198.0,
                original_price=298.0,
                category=SaleCategory.MEAT,
                valid_from=now,
                valid_until=now + timedelta(days=1),
            ),
            SaleItem(
                id="item-004",
                store_name="西友",
                product_name="牛乳",
                price=168.0,
                category=SaleCategory.DAIRY,
                valid_from=now,
                valid_until=now + timedelta(days=5),
            ),
        ]

    def test_add_sale_item(self, service):
        """特売商品の追加"""
        item = SaleItem(
            id="test-001",
            store_name="テストスーパー",
            product_name="テスト商品",
            price=100.0,
        )

        service.add_sale_item(item)
        assert len(service.sale_items) == 1
        assert service.sale_items[0].id == "test-001"

    def test_get_active_sales_no_filter(self, service, sample_items):
        """フィルタなしで有効な特売情報を取得"""
        for item in sample_items:
            service.add_sale_item(item)

        active_sales = service.get_active_sales()
        assert len(active_sales) == 4

    def test_get_active_sales_filter_by_store(self, service, sample_items):
        """店舗名でフィルタリング"""
        for item in sample_items:
            service.add_sale_item(item)

        active_sales = service.get_active_sales(store_name="イオン")
        assert len(active_sales) == 2
        assert all(item.store_name == "イオン" for item in active_sales)

    def test_get_active_sales_filter_by_category(self, service, sample_items):
        """カテゴリでフィルタリング"""
        for item in sample_items:
            service.add_sale_item(item)

        active_sales = service.get_active_sales(category=SaleCategory.VEGETABLE)
        assert len(active_sales) == 2
        assert all(item.category == SaleCategory.VEGETABLE for item in active_sales)

    def test_get_active_sales_filter_by_min_discount(self, service, sample_items):
        """最小割引率でフィルタリング"""
        for item in sample_items:
            service.add_sale_item(item)

        active_sales = service.get_active_sales(min_discount=30.0)
        assert len(active_sales) == 2  # たまねぎ（イオン）34.7%、豚肉 33.6%

    def test_get_active_sales_sorted_by_discount(self, service, sample_items):
        """割引率の高い順にソート"""
        for item in sample_items:
            service.add_sale_item(item)

        active_sales = service.get_active_sales()

        # 割引率が設定されているアイテムのみ確認
        discounted = [item for item in active_sales if item.discount_rate]
        for i in range(len(discounted) - 1):
            assert discounted[i].discount_rate >= discounted[i + 1].discount_rate

    def test_compare_prices(self, service, sample_items):
        """価格比較"""
        for item in sample_items:
            service.add_sale_item(item)

        comparison = service.compare_prices("たまねぎ")
        assert len(comparison) == 2
        assert comparison[0]["price"] == 98.0  # イオンが最安
        assert comparison[0]["store_name"] == "イオン"

    def test_normalize_ingredient_name(self, service):
        """商品名の正規化"""
        assert service.normalize_ingredient_name("たまねぎ") == "たまねぎ"
        assert service.normalize_ingredient_name("玉ねぎ") == "たまねぎ"
        assert service.normalize_ingredient_name("国産玉ねぎ") == "たまねぎ"
        assert service.normalize_ingredient_name("豚バラ肉") == "豚肉"
        assert service.normalize_ingredient_name("不明な商品") is None

    def test_get_ingredient_recommendations(self, service, sample_items):
        """材料からのおすすめ取得"""
        for item in sample_items:
            service.add_sale_item(item)

        recommendations = service.get_ingredient_recommendations(
            ["たまねぎ", "豚肉", "にんじん"]
        )

        assert len(recommendations) == 3  # たまねぎ2件、豚肉1件
        # 割引率の高い順
        assert recommendations[0].discount_rate >= recommendations[1].discount_rate

    def test_get_recipe_cost_estimate(self, service, sample_items):
        """レシピ材料費見積もり"""
        for item in sample_items:
            service.add_sale_item(item)

        estimate = service.get_recipe_cost_estimate(["たまねぎ", "豚肉", "にんじん"])

        assert estimate["ingredients_count"] == 3
        assert estimate["available_on_sale"] == 2  # たまねぎ、豚肉
        assert estimate["total_cost"] == 98.0 + 198.0  # 最安値の合計
        assert estimate["coverage_rate"] == pytest.approx(66.7, rel=0.1)

    def test_clear_expired_sales(self, service):
        """期限切れ特売情報の削除"""
        now = datetime.now()

        # 有効なアイテム
        valid_item = SaleItem(
            id="valid-001",
            store_name="テストスーパー",
            product_name="有効商品",
            price=100.0,
            valid_from=now,
            valid_until=now + timedelta(days=1),
        )

        # 期限切れアイテム
        expired_item = SaleItem(
            id="expired-001",
            store_name="テストスーパー",
            product_name="期限切れ商品",
            price=100.0,
            valid_from=now - timedelta(days=5),
            valid_until=now - timedelta(days=1),
        )

        service.add_sale_item(valid_item)
        service.add_sale_item(expired_item)

        assert len(service.sale_items) == 2

        deleted_count = service.clear_expired_sales()

        assert deleted_count == 1
        assert len(service.sale_items) == 1
        assert service.sale_items[0].id == "valid-001"

    def test_get_statistics(self, service, sample_items):
        """統計情報の取得"""
        for item in sample_items:
            service.add_sale_item(item)

        stats = service.get_statistics()

        assert stats["total_active_sales"] == 4
        assert stats["total_all_sales"] == 4
        assert stats["average_discount_rate"] > 0
        assert "categories" in stats
        assert "stores" in stats
        assert stats["categories"]["vegetable"] == 2
        assert stats["stores"]["イオン"] == 2

    def test_get_statistics_empty(self, service):
        """空の統計情報"""
        stats = service.get_statistics()

        assert stats["total_active_sales"] == 0
        assert stats["total_all_sales"] == 0
        assert stats["average_discount_rate"] == 0
        assert stats["categories"] == {}
        assert stats["stores"] == {}


class TestIntegration:
    """統合テスト"""

    def test_full_workflow(self):
        """完全なワークフローテスト"""
        service = SaleService()

        # 1. 特売情報追加
        now = datetime.now()
        items = [
            SaleItem(
                id=f"item-{i}",
                store_name="統合テストスーパー",
                product_name=f"商品{i}",
                price=100.0 * i,
                original_price=150.0 * i,
                category=SaleCategory.VEGETABLE,
                valid_from=now,
                valid_until=now + timedelta(days=3),
            )
            for i in range(1, 6)
        ]

        for item in items:
            service.add_sale_item(item)

        # 2. 取得
        active = service.get_active_sales()
        assert len(active) == 5

        # 3. 統計
        stats = service.get_statistics()
        assert stats["total_active_sales"] == 5

        # 4. フィルタ
        filtered = service.get_active_sales(min_discount=30.0)
        assert all(item.discount_rate >= 30.0 for item in filtered)

        # 5. 期限切れ削除（全て有効なので削除なし）
        deleted = service.clear_expired_sales()
        assert deleted == 0
