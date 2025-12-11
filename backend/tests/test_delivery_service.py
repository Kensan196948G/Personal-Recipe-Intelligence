"""
宅配サービス連携サービステスト
"""

import pytest
import json
import tempfile
from pathlib import Path

from backend.services.delivery_service import (
  DeliveryService,
  DeliveryServiceType,
  DeliveryProduct,
  CartItem,
  DeliveryCart
)


@pytest.fixture
def temp_data_dir():
  """一時データディレクトリ"""
  with tempfile.TemporaryDirectory() as tmpdir:
    yield tmpdir


@pytest.fixture
def delivery_service(temp_data_dir):
  """DeliveryServiceインスタンス"""
  return DeliveryService(data_dir=temp_data_dir)


class TestDeliveryService:
  """DeliveryServiceテスト"""

  def test_get_available_services(self, delivery_service):
    """対応サービス一覧取得"""
    services = delivery_service.get_available_services()

    assert len(services) > 0
    assert all("id" in s for s in services)
    assert all("name" in s for s in services)
    assert all("delivery_fee" in s for s in services)

    # 各サービスが含まれているか
    service_ids = [s["id"] for s in services]
    assert DeliveryServiceType.AEON in service_ids
    assert DeliveryServiceType.SEIYU in service_ids
    assert DeliveryServiceType.RAKUTEN in service_ids

  def test_search_products_basic(self, delivery_service):
    """基本的な商品検索"""
    products = delivery_service.search_products("玉ねぎ")

    assert len(products) > 0
    assert all(isinstance(p, DeliveryProduct) for p in products)
    assert all("玉ねぎ" in p.name or "玉ねぎ" in p.name.lower() for p in products)

  def test_search_products_with_service_filter(self, delivery_service):
    """サービスフィルタ付き検索"""
    products = delivery_service.search_products(
      "玉ねぎ",
      services=[DeliveryServiceType.AEON]
    )

    assert len(products) > 0
    assert all(p.service == DeliveryServiceType.AEON for p in products)

  def test_search_products_normalization(self, delivery_service):
    """食材名正規化のテスト"""
    # ひらがな
    products1 = delivery_service.search_products("たまねぎ")
    # カタカナ
    products2 = delivery_service.search_products("タマネギ")
    # 漢字
    products3 = delivery_service.search_products("玉ねぎ")

    # すべて同じ商品がヒットするはず
    assert len(products1) > 0
    assert len(products2) > 0
    assert len(products3) > 0

  def test_search_products_max_results(self, delivery_service):
    """最大取得件数制限"""
    products = delivery_service.search_products("玉ねぎ", max_results=2)

    assert len(products) <= 2

  def test_search_products_not_found(self, delivery_service):
    """商品が見つからない場合"""
    products = delivery_service.search_products("存在しない食材xyz")

    assert len(products) == 0

  def test_add_to_cart(self, delivery_service):
    """カートに追加"""
    # 商品検索
    products = delivery_service.search_products("玉ねぎ")
    assert len(products) > 0

    product = products[0]

    # カートに追加
    result = delivery_service.add_to_cart(
      service=product.service,
      product_id=product.id,
      quantity=2
    )

    assert result["status"] == "ok"
    assert result["cart"]["item_count"] == 1
    assert result["cart"]["total_price"] == product.price * 2

  def test_add_to_cart_multiple_items(self, delivery_service):
    """複数商品をカートに追加"""
    products = delivery_service.search_products("玉ねぎ")
    assert len(products) > 0

    service = products[0].service

    # 複数商品追加
    for i in range(min(3, len(products))):
      delivery_service.add_to_cart(
        service=service,
        product_id=products[i].id,
        quantity=1
      )

    # カート確認
    cart = delivery_service.get_cart(service)
    assert cart["item_count"] == min(3, len(products))
    assert cart["total_price"] > 0

  def test_add_to_cart_same_product_twice(self, delivery_service):
    """同じ商品を複数回追加"""
    products = delivery_service.search_products("玉ねぎ")
    assert len(products) > 0

    product = products[0]

    # 1回目
    delivery_service.add_to_cart(
      service=product.service,
      product_id=product.id,
      quantity=1
    )

    # 2回目
    result = delivery_service.add_to_cart(
      service=product.service,
      product_id=product.id,
      quantity=2
    )

    # 数量が合算されているか
    cart = result["cart"]
    item = next(i for i in cart["items"] if i["product"]["id"] == product.id)
    assert item["quantity"] == 3

  def test_add_to_cart_invalid_product(self, delivery_service):
    """存在しない商品をカートに追加"""
    with pytest.raises(ValueError, match="Product not found"):
      delivery_service.add_to_cart(
        service=DeliveryServiceType.AEON,
        product_id="invalid_product_id",
        quantity=1
      )

  def test_get_cart_empty(self, delivery_service):
    """空のカート取得"""
    cart = delivery_service.get_cart(DeliveryServiceType.AEON)

    assert cart["service"] == DeliveryServiceType.AEON
    assert cart["item_count"] == 0
    assert cart["total_price"] == 0.0
    assert len(cart["items"]) == 0

  def test_remove_from_cart(self, delivery_service):
    """カートから削除"""
    # 商品追加
    products = delivery_service.search_products("玉ねぎ")
    product = products[0]

    delivery_service.add_to_cart(
      service=product.service,
      product_id=product.id,
      quantity=1
    )

    # 削除
    result = delivery_service.remove_from_cart(
      service=product.service,
      product_id=product.id
    )

    assert result["status"] == "ok"
    assert result["cart"]["item_count"] == 0

  def test_clear_cart(self, delivery_service):
    """カートクリア"""
    # 複数商品追加
    products = delivery_service.search_products("玉ねぎ")
    service = products[0].service

    for product in products[:3]:
      delivery_service.add_to_cart(
        service=service,
        product_id=product.id,
        quantity=1
      )

    # クリア
    result = delivery_service.clear_cart(service)

    assert result["status"] == "ok"
    assert result["cart"]["item_count"] == 0
    assert result["cart"]["total_price"] == 0.0

  def test_generate_checkout_url(self, delivery_service):
    """注文ページURL生成"""
    # 商品追加
    products = delivery_service.search_products("玉ねぎ")
    product = products[0]

    delivery_service.add_to_cart(
      service=product.service,
      product_id=product.id,
      quantity=1
    )

    # URL生成
    url = delivery_service.generate_checkout_url(product.service)

    assert url is not None
    assert isinstance(url, str)
    assert url.startswith("http")
    assert "cart" in url

  def test_generate_checkout_url_empty_cart(self, delivery_service):
    """空のカートで注文ページURL生成"""
    with pytest.raises(ValueError, match="Cart is empty"):
      delivery_service.generate_checkout_url(DeliveryServiceType.AEON)

  def test_compare_prices(self, delivery_service):
    """価格比較"""
    result = delivery_service.compare_prices("玉ねぎ")

    assert result["ingredient"] == "玉ねぎ"
    assert len(result["products"]) > 0
    assert "best_price" in result
    assert "price_range" in result
    assert "by_service" in result

    # 最安値チェック
    best = result["best_price"]
    assert "product" in best
    assert "service" in best
    assert "price" in best

    # 価格範囲チェック
    price_range = result["price_range"]
    assert price_range["min"] is not None
    assert price_range["max"] is not None
    assert price_range["avg"] is not None
    assert price_range["min"] <= price_range["avg"] <= price_range["max"]

  def test_compare_prices_no_results(self, delivery_service):
    """商品が見つからない場合の価格比較"""
    result = delivery_service.compare_prices("存在しない食材xyz")

    assert result["ingredient"] == "存在しない食材xyz"
    assert len(result["products"]) == 0
    assert result["best_price"] is None
    assert result["price_range"] is None

  def test_cart_persistence(self, delivery_service):
    """カートの永続化"""
    # 商品追加
    products = delivery_service.search_products("玉ねぎ")
    product = products[0]

    delivery_service.add_to_cart(
      service=product.service,
      product_id=product.id,
      quantity=2
    )

    # 新しいインスタンスで読み込み
    delivery_service2 = DeliveryService(data_dir=delivery_service.data_dir)
    cart = delivery_service2.get_cart(product.service)

    assert cart["item_count"] == 1
    assert cart["items"][0]["quantity"] == 2
    assert cart["items"][0]["product"]["id"] == product.id

  def test_multiple_services_cart(self, delivery_service):
    """複数サービスのカート管理"""
    # イオンのカート
    aeon_products = delivery_service.search_products(
      "玉ねぎ",
      services=[DeliveryServiceType.AEON]
    )
    if aeon_products:
      delivery_service.add_to_cart(
        service=DeliveryServiceType.AEON,
        product_id=aeon_products[0].id,
        quantity=1
      )

    # 西友のカート
    seiyu_products = delivery_service.search_products(
      "玉ねぎ",
      services=[DeliveryServiceType.SEIYU]
    )
    if seiyu_products:
      delivery_service.add_to_cart(
        service=DeliveryServiceType.SEIYU,
        product_id=seiyu_products[0].id,
        quantity=2
      )

    # それぞれのカート確認
    aeon_cart = delivery_service.get_cart(DeliveryServiceType.AEON)
    seiyu_cart = delivery_service.get_cart(DeliveryServiceType.SEIYU)

    assert aeon_cart["item_count"] == 1
    assert seiyu_cart["item_count"] == 1
    assert aeon_cart["items"][0]["quantity"] == 1
    assert seiyu_cart["items"][0]["quantity"] == 2

  def test_normalize_ingredient_name(self, delivery_service):
    """食材名正規化の詳細テスト"""
    test_cases = [
      ("たまねぎ", "玉ねぎ"),
      ("タマネギ", "玉ねぎ"),
      ("ぶたにく", "豚肉"),
      ("ブタニク", "豚肉"),
      ("しょうゆ", "醤油"),
      ("ショウユ", "醤油"),
    ]

    for input_name, expected in test_cases:
      normalized = delivery_service._normalize_ingredient_name(input_name)
      assert expected in normalized or normalized in expected

  def test_product_sorting(self, delivery_service):
    """商品ソートのテスト"""
    products = delivery_service.search_products("玉ねぎ")

    # 在庫あり商品が先に来る
    in_stock_products = [p for p in products if p.in_stock]
    out_of_stock_products = [p for p in products if not p.in_stock]

    if in_stock_products and out_of_stock_products:
      # 在庫ありの最後の商品 < 在庫なしの最初の商品のインデックス
      last_in_stock_idx = products.index(in_stock_products[-1])
      first_out_of_stock_idx = products.index(out_of_stock_products[0])
      assert last_in_stock_idx < first_out_of_stock_idx

    # 在庫あり商品は価格順
    if len(in_stock_products) > 1:
      for i in range(len(in_stock_products) - 1):
        assert in_stock_products[i].price <= in_stock_products[i + 1].price


class TestDeliveryProduct:
  """DeliveryProductテスト"""

  def test_product_creation(self):
    """商品インスタンス生成"""
    product = DeliveryProduct(
      id="test_001",
      service=DeliveryServiceType.AEON,
      name="テスト商品",
      price=100.0,
      unit="個",
      category="テスト",
      in_stock=True
    )

    assert product.id == "test_001"
    assert product.service == DeliveryServiceType.AEON
    assert product.name == "テスト商品"
    assert product.price == 100.0
    assert product.in_stock is True


class TestCartItem:
  """CartItemテスト"""

  def test_cart_item_creation(self):
    """カートアイテム生成"""
    product = DeliveryProduct(
      id="test_001",
      service=DeliveryServiceType.AEON,
      name="テスト商品",
      price=100.0,
      unit="個",
      category="テスト",
      in_stock=True
    )

    item = CartItem(
      product=product,
      quantity=3,
      added_at="2025-12-11T00:00:00"
    )

    assert item.product.id == "test_001"
    assert item.quantity == 3
    assert item.added_at == "2025-12-11T00:00:00"
