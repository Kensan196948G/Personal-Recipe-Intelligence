"""
宅配サービス連携サービス

ネットスーパー・宅配サービスとの連携機能を提供
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class DeliveryServiceType(str, Enum):
    """宅配サービス種別"""

    AEON = "aeon"
    SEIYU = "seiyu"
    RAKUTEN = "rakuten"
    AMAZON_FRESH = "amazon_fresh"
    OKA_MART = "oka_mart"


@dataclass
class DeliveryProduct:
    """宅配商品"""

    id: str
    service: DeliveryServiceType
    name: str
    price: float
    unit: str
    category: str
    in_stock: bool
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    affiliate_url: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None


@dataclass
class CartItem:
    """カート商品"""

    product: DeliveryProduct
    quantity: int
    added_at: str


@dataclass
class DeliveryCart:
    """宅配カート"""

    service: DeliveryServiceType
    items: List[CartItem]
    total_price: float
    created_at: str
    updated_at: str


class DeliveryService:
    """宅配サービス連携サービス"""

    def __init__(self, data_dir: str = "data/delivery"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cart_file = self.data_dir / "cart.json"
        self.products_file = self.data_dir / "products_mock.json"
        self._init_mock_data()

    def _init_mock_data(self) -> None:
        """モックデータ初期化"""
        if not self.products_file.exists():
            mock_products = self._generate_mock_products()
            with open(self.products_file, "w", encoding="utf-8") as f:
                json.dump(mock_products, f, ensure_ascii=False, indent=2)

    def _generate_mock_products(self) -> List[Dict[str, Any]]:
        """モック商品データ生成"""
        products = []

        # イオン
        products.extend(
            [
                {
                    "id": "aeon_001",
                    "service": "aeon",
                    "name": "トップバリュ 玉ねぎ 3個入",
                    "price": 198,
                    "unit": "袋",
                    "category": "野菜",
                    "in_stock": True,
                    "image_url": "https://example.com/aeon/onion.jpg",
                    "product_url": "https://shop.aeon.com/netsuper/01234",
                    "brand": "トップバリュ",
                },
                {
                    "id": "aeon_002",
                    "service": "aeon",
                    "name": "国産 豚肉 こま切れ 300g",
                    "price": 498,
                    "unit": "パック",
                    "category": "肉",
                    "in_stock": True,
                    "product_url": "https://shop.aeon.com/netsuper/01235",
                    "brand": "イオン",
                },
                {
                    "id": "aeon_003",
                    "service": "aeon",
                    "name": "キッコーマン 醤油 1L",
                    "price": 328,
                    "unit": "本",
                    "category": "調味料",
                    "in_stock": True,
                    "product_url": "https://shop.aeon.com/netsuper/01236",
                    "brand": "キッコーマン",
                },
            ]
        )

        # 西友
        products.extend(
            [
                {
                    "id": "seiyu_001",
                    "service": "seiyu",
                    "name": "みなさまのお墨付き 玉ねぎ 3個",
                    "price": 178,
                    "unit": "袋",
                    "category": "野菜",
                    "in_stock": True,
                    "product_url": "https://www.seiyu.co.jp/item/12345",
                    "brand": "みなさまのお墨付き",
                },
                {
                    "id": "seiyu_002",
                    "service": "seiyu",
                    "name": "国産豚肉 切り落とし 300g",
                    "price": 478,
                    "unit": "パック",
                    "category": "肉",
                    "in_stock": True,
                    "product_url": "https://www.seiyu.co.jp/item/12346",
                },
                {
                    "id": "seiyu_003",
                    "service": "seiyu",
                    "name": "キッコーマン しょうゆ 1L",
                    "price": 318,
                    "unit": "本",
                    "category": "調味料",
                    "in_stock": True,
                    "product_url": "https://www.seiyu.co.jp/item/12347",
                    "brand": "キッコーマン",
                },
            ]
        )

        # 楽天
        products.extend(
            [
                {
                    "id": "rakuten_001",
                    "service": "rakuten",
                    "name": "北海道産 玉ねぎ 5kg",
                    "price": 1980,
                    "unit": "箱",
                    "category": "野菜",
                    "in_stock": True,
                    "product_url": "https://item.rakuten.co.jp/shop/item001",
                    "affiliate_url": "https://hb.afl.rakuten.co.jp/...",
                    "brand": "北海道直送",
                },
                {
                    "id": "rakuten_002",
                    "service": "rakuten",
                    "name": "鹿児島県産 豚肉 こま切れ 1kg",
                    "price": 1580,
                    "unit": "パック",
                    "category": "肉",
                    "in_stock": True,
                    "product_url": "https://item.rakuten.co.jp/shop/item002",
                    "affiliate_url": "https://hb.afl.rakuten.co.jp/...",
                },
            ]
        )

        # Amazon Fresh
        products.extend(
            [
                {
                    "id": "amazon_001",
                    "service": "amazon_fresh",
                    "name": "玉ねぎ 3個入",
                    "price": 188,
                    "unit": "袋",
                    "category": "野菜",
                    "in_stock": True,
                    "product_url": "https://www.amazon.co.jp/dp/ASIN001",
                    "brand": "Amazon Fresh",
                },
                {
                    "id": "amazon_002",
                    "service": "amazon_fresh",
                    "name": "豚肉 こま切れ 300g",
                    "price": 528,
                    "unit": "パック",
                    "category": "肉",
                    "in_stock": True,
                    "product_url": "https://www.amazon.co.jp/dp/ASIN002",
                },
            ]
        )

        # オーケーマート
        products.extend(
            [
                {
                    "id": "oka_001",
                    "service": "oka_mart",
                    "name": "玉ねぎ（中玉）3個",
                    "price": 158,
                    "unit": "袋",
                    "category": "野菜",
                    "in_stock": True,
                    "product_url": "https://ok-mart.jp/products/001",
                },
                {
                    "id": "oka_002",
                    "service": "oka_mart",
                    "name": "豚肉 切り落とし 300g",
                    "price": 448,
                    "unit": "パック",
                    "category": "肉",
                    "in_stock": True,
                    "product_url": "https://ok-mart.jp/products/002",
                },
            ]
        )

        return products

    def get_available_services(self) -> List[Dict[str, Any]]:
        """対応サービス一覧取得"""
        services = [
            {
                "id": DeliveryServiceType.AEON,
                "name": "イオンネットスーパー",
                "description": "全国展開のネットスーパー",
                "logo_url": "https://example.com/logos/aeon.png",
                "min_order": 700,
                "delivery_fee": 330,
                "free_shipping_threshold": 5000,
                "regions": ["全国（一部地域除く）"],
            },
            {
                "id": DeliveryServiceType.SEIYU,
                "name": "西友ネットスーパー",
                "description": "楽天グループのネットスーパー",
                "logo_url": "https://example.com/logos/seiyu.png",
                "min_order": 0,
                "delivery_fee": 330,
                "free_shipping_threshold": 5500,
                "regions": ["関東・関西中心"],
            },
            {
                "id": DeliveryServiceType.RAKUTEN,
                "name": "楽天西友ネットスーパー",
                "description": "楽天ポイントが貯まる",
                "logo_url": "https://example.com/logos/rakuten.png",
                "min_order": 0,
                "delivery_fee": 330,
                "free_shipping_threshold": 5500,
                "regions": ["全国"],
            },
            {
                "id": DeliveryServiceType.AMAZON_FRESH,
                "name": "Amazon Fresh",
                "description": "Amazonの生鮮食品配送",
                "logo_url": "https://example.com/logos/amazon.png",
                "min_order": 4000,
                "delivery_fee": 390,
                "free_shipping_threshold": 10000,
                "regions": ["東京・神奈川・千葉中心"],
            },
            {
                "id": DeliveryServiceType.OKA_MART,
                "name": "オーケーネットスーパー",
                "description": "毎日安い価格",
                "logo_url": "https://example.com/logos/oka.png",
                "min_order": 1500,
                "delivery_fee": 300,
                "free_shipping_threshold": None,
                "regions": ["関東中心"],
            },
        ]
        return services

    def search_products(
        self,
        ingredient_name: str,
        services: Optional[List[DeliveryServiceType]] = None,
        max_results: int = 20,
    ) -> List[DeliveryProduct]:
        """商品検索"""
        # 食材名の正規化
        normalized_name = self._normalize_ingredient_name(ingredient_name)

        # モックデータから検索
        with open(self.products_file, "r", encoding="utf-8") as f:
            all_products = json.load(f)

        results = []
        for product_data in all_products:
            # サービスフィルタ
            if services and product_data["service"] not in services:
                continue

            # 名前マッチング
            product_name_normalized = self._normalize_ingredient_name(
                product_data["name"]
            )
            if self._match_ingredient(normalized_name, product_name_normalized):
                product = DeliveryProduct(**product_data)
                results.append(product)

        # 在庫あり優先、価格順でソート
        results.sort(key=lambda p: (not p.in_stock, p.price))

        return results[:max_results]

    def _normalize_ingredient_name(self, name: str) -> str:
        """食材名正規化"""
        # ひらがな・カタカナ統一、スペース削除など
        normalized = name.lower()
        normalized = re.sub(r"[\s　]+", "", normalized)

        # よくある表記ゆれを統一
        replacements = {
            "たまねぎ": "玉ねぎ",
            "タマネギ": "玉ねぎ",
            "ぶたにく": "豚肉",
            "ブタニク": "豚肉",
            "しょうゆ": "醤油",
            "ショウユ": "醤油",
            "さとう": "砂糖",
            "サトウ": "砂糖",
            "しお": "塩",
            "シオ": "塩",
        }

        for old, new in replacements.items():
            normalized = normalized.replace(old, new)

        return normalized

    def _match_ingredient(self, ingredient: str, product_name: str) -> bool:
        """食材と商品名のマッチング"""
        # 部分一致で判定
        return ingredient in product_name or product_name in ingredient

    def add_to_cart(
        self, service: DeliveryServiceType, product_id: str, quantity: int = 1
    ) -> Dict[str, Any]:
        """カートに追加"""
        # 商品検索
        with open(self.products_file, "r", encoding="utf-8") as f:
            all_products = json.load(f)

        product_data = next((p for p in all_products if p["id"] == product_id), None)

        if not product_data:
            raise ValueError(f"Product not found: {product_id}")

        product = DeliveryProduct(**product_data)

        # カート読み込み
        cart = self._load_cart(service)

        # 既存商品チェック
        existing_item = next(
            (item for item in cart.items if item.product.id == product_id), None
        )

        now = datetime.now().isoformat()

        if existing_item:
            existing_item.quantity += quantity
        else:
            cart_item = CartItem(product=product, quantity=quantity, added_at=now)
            cart.items.append(cart_item)

        # 合計金額更新
        cart.total_price = sum(
            item.product.price * item.quantity for item in cart.items
        )
        cart.updated_at = now

        # 保存
        self._save_cart(cart)

        return {
            "status": "ok",
            "message": f"Added {quantity}x {product.name} to cart",
            "cart": self._cart_to_dict(cart),
        }

    def get_cart(self, service: DeliveryServiceType) -> Dict[str, Any]:
        """カート内容取得"""
        cart = self._load_cart(service)
        return self._cart_to_dict(cart)

    def remove_from_cart(
        self, service: DeliveryServiceType, product_id: str
    ) -> Dict[str, Any]:
        """カートから削除"""
        cart = self._load_cart(service)

        cart.items = [item for item in cart.items if item.product.id != product_id]

        # 合計金額更新
        cart.total_price = sum(
            item.product.price * item.quantity for item in cart.items
        )
        cart.updated_at = datetime.now().isoformat()

        self._save_cart(cart)

        return {
            "status": "ok",
            "message": "Item removed from cart",
            "cart": self._cart_to_dict(cart),
        }

    def clear_cart(self, service: DeliveryServiceType) -> Dict[str, Any]:
        """カートクリア"""
        cart = DeliveryCart(
            service=service,
            items=[],
            total_price=0.0,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        self._save_cart(cart)

        return {
            "status": "ok",
            "message": "Cart cleared",
            "cart": self._cart_to_dict(cart),
        }

    def generate_checkout_url(self, service: DeliveryServiceType) -> str:
        """注文ページURL生成"""
        cart = self._load_cart(service)

        if not cart.items:
            raise ValueError("Cart is empty")

        # サービスごとのベースURL
        base_urls = {
            DeliveryServiceType.AEON: "https://shop.aeon.com/netsuper/cart",
            DeliveryServiceType.SEIYU: "https://www.seiyu.co.jp/cart",
            DeliveryServiceType.RAKUTEN: "https://netsuper.rakuten.co.jp/cart",
            DeliveryServiceType.AMAZON_FRESH: "https://www.amazon.co.jp/afx/cart",
            DeliveryServiceType.OKA_MART: "https://ok-mart.jp/cart",
        }

        base_url = base_urls.get(service)
        if not base_url:
            raise ValueError(f"Unsupported service: {service}")

        # 商品IDリストをクエリパラメータに追加（実際のAPIでは異なる）
        product_ids = [item.product.id for item in cart.items]
        url = f"{base_url}?items={','.join(product_ids)}"

        return url

    def compare_prices(self, ingredient_name: str) -> Dict[str, Any]:
        """価格比較"""
        products = self.search_products(ingredient_name)

        if not products:
            return {
                "ingredient": ingredient_name,
                "products": [],
                "best_price": None,
                "price_range": None,
            }

        # サービスごとにグループ化
        by_service: Dict[str, List[DeliveryProduct]] = {}
        for product in products:
            service_name = product.service
            if service_name not in by_service:
                by_service[service_name] = []
            by_service[service_name].append(product)

        # 最安値
        best_product = min(products, key=lambda p: p.price)

        # 価格範囲
        prices = [p.price for p in products if p.in_stock]
        price_range = {
            "min": min(prices) if prices else None,
            "max": max(prices) if prices else None,
            "avg": sum(prices) / len(prices) if prices else None,
        }

        return {
            "ingredient": ingredient_name,
            "products": [self._product_to_dict(p) for p in products],
            "by_service": {
                service: [self._product_to_dict(p) for p in prods]
                for service, prods in by_service.items()
            },
            "best_price": {
                "product": self._product_to_dict(best_product),
                "service": best_product.service,
                "price": best_product.price,
            },
            "price_range": price_range,
        }

    def _load_cart(self, service: DeliveryServiceType) -> DeliveryCart:
        """カート読み込み"""
        if not self.cart_file.exists():
            return DeliveryCart(
                service=service,
                items=[],
                total_price=0.0,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            )

        with open(self.cart_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # サービスごとのカート
        service_data = data.get(service, None)
        if not service_data:
            return DeliveryCart(
                service=service,
                items=[],
                total_price=0.0,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            )

        items = [
            CartItem(
                product=DeliveryProduct(**item["product"]),
                quantity=item["quantity"],
                added_at=item["added_at"],
            )
            for item in service_data["items"]
        ]

        return DeliveryCart(
            service=service,
            items=items,
            total_price=service_data["total_price"],
            created_at=service_data["created_at"],
            updated_at=service_data["updated_at"],
        )

    def _save_cart(self, cart: DeliveryCart) -> None:
        """カート保存"""
        # 全サービスのカートを読み込み
        if self.cart_file.exists():
            with open(self.cart_file, "r", encoding="utf-8") as f:
                all_carts = json.load(f)
        else:
            all_carts = {}

        # 該当サービスのカートを更新
        all_carts[cart.service] = self._cart_to_dict(cart)

        with open(self.cart_file, "w", encoding="utf-8") as f:
            json.dump(all_carts, f, ensure_ascii=False, indent=2)

    def _product_to_dict(self, product: DeliveryProduct) -> Dict[str, Any]:
        """商品を辞書に変換"""
        return asdict(product)

    def _cart_to_dict(self, cart: DeliveryCart) -> Dict[str, Any]:
        """カートを辞書に変換"""
        return {
            "service": cart.service,
            "items": [
                {
                    "product": self._product_to_dict(item.product),
                    "quantity": item.quantity,
                    "added_at": item.added_at,
                }
                for item in cart.items
            ],
            "total_price": cart.total_price,
            "item_count": len(cart.items),
            "created_at": cart.created_at,
            "updated_at": cart.updated_at,
        }
