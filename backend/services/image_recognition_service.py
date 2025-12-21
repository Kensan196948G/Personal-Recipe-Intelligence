"""
画像認識サービス - 食材識別機能

外部AI APIとの統合準備を含む、食材画像認識サービス
モックモード（デモ用）と本番モードを切り替え可能
"""

import base64
import hashlib
import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image

logger = logging.getLogger(__name__)


class ImageRecognitionService:
    """画像認識サービス - 食材識別"""

    # 日本の一般的な食材辞書（100種類）
    INGREDIENT_DICTIONARY = {
        # 野菜
        "tomato": {"ja": "トマト", "category": "野菜", "keywords": ["赤", "丸い"]},
        "onion": {"ja": "玉ねぎ", "category": "野菜", "keywords": ["茶色", "球"]},
        "carrot": {
            "ja": "にんじん",
            "category": "野菜",
            "keywords": ["オレンジ", "長い"],
        },
        "potato": {
            "ja": "じゃがいも",
            "category": "野菜",
            "keywords": ["茶色", "丸い"],
        },
        "cabbage": {"ja": "キャベツ", "category": "野菜", "keywords": ["緑", "丸い"]},
        "lettuce": {"ja": "レタス", "category": "野菜", "keywords": ["緑", "葉"]},
        "cucumber": {"ja": "きゅうり", "category": "野菜", "keywords": ["緑", "長い"]},
        "eggplant": {"ja": "なす", "category": "野菜", "keywords": ["紫", "長い"]},
        "bell_pepper": {
            "ja": "ピーマン",
            "category": "野菜",
            "keywords": ["緑", "小さい"],
        },
        "broccoli": {
            "ja": "ブロッコリー",
            "category": "野菜",
            "keywords": ["緑", "房"],
        },
        "spinach": {"ja": "ほうれん草", "category": "野菜", "keywords": ["緑", "葉"]},
        "chinese_cabbage": {"ja": "白菜", "category": "野菜", "keywords": ["白", "葉"]},
        "daikon": {"ja": "大根", "category": "野菜", "keywords": ["白", "長い"]},
        "leek": {"ja": "ねぎ", "category": "野菜", "keywords": ["白緑", "長い"]},
        "garlic": {"ja": "にんにく", "category": "野菜", "keywords": ["白", "小さい"]},
        "ginger": {"ja": "しょうが", "category": "野菜", "keywords": ["茶色", "塊"]},
        "green_onion": {"ja": "青ねぎ", "category": "野菜", "keywords": ["緑", "細い"]},
        "mushroom": {"ja": "しいたけ", "category": "野菜", "keywords": ["茶色", "傘"]},
        "enoki": {"ja": "えのき", "category": "野菜", "keywords": ["白", "細長い"]},
        "shimeji": {"ja": "しめじ", "category": "野菜", "keywords": ["茶色", "小さい"]},
        # 肉類
        "chicken": {"ja": "鶏肉", "category": "肉類", "keywords": ["ピンク", "肉"]},
        "pork": {"ja": "豚肉", "category": "肉類", "keywords": ["ピンク", "肉"]},
        "beef": {"ja": "牛肉", "category": "肉類", "keywords": ["赤", "肉"]},
        "ground_meat": {
            "ja": "ひき肉",
            "category": "肉類",
            "keywords": ["赤", "細かい"],
        },
        "bacon": {"ja": "ベーコン", "category": "肉類", "keywords": ["ピンク", "薄い"]},
        "sausage": {"ja": "ソーセージ", "category": "肉類", "keywords": ["茶色", "棒"]},
        "ham": {"ja": "ハム", "category": "肉類", "keywords": ["ピンク", "薄い"]},
        # 魚介類
        "salmon": {"ja": "鮭", "category": "魚介類", "keywords": ["オレンジ", "魚"]},
        "tuna": {"ja": "まぐろ", "category": "魚介類", "keywords": ["赤", "魚"]},
        "mackerel": {"ja": "さば", "category": "魚介類", "keywords": ["銀", "魚"]},
        "sardine": {"ja": "いわし", "category": "魚介類", "keywords": ["銀", "小さい"]},
        "squid": {"ja": "イカ", "category": "魚介類", "keywords": ["白", "軟体"]},
        "octopus": {"ja": "タコ", "category": "魚介類", "keywords": ["赤", "軟体"]},
        "shrimp": {
            "ja": "エビ",
            "category": "魚介類",
            "keywords": ["ピンク", "曲がった"],
        },
        "crab": {"ja": "カニ", "category": "魚介類", "keywords": ["赤", "甲殻"]},
        "clam": {"ja": "あさり", "category": "魚介類", "keywords": ["茶色", "貝"]},
        "scallop": {"ja": "ホタテ", "category": "魚介類", "keywords": ["白", "貝"]},
        # 卵・乳製品
        "egg": {"ja": "卵", "category": "卵・乳製品", "keywords": ["白", "楕円"]},
        "milk": {"ja": "牛乳", "category": "卵・乳製品", "keywords": ["白", "液体"]},
        "cheese": {
            "ja": "チーズ",
            "category": "卵・乳製品",
            "keywords": ["黄色", "固形"],
        },
        "butter": {
            "ja": "バター",
            "category": "卵・乳製品",
            "keywords": ["黄色", "固形"],
        },
        "yogurt": {
            "ja": "ヨーグルト",
            "category": "卵・乳製品",
            "keywords": ["白", "液体"],
        },
        # 穀物・麺類
        "rice": {"ja": "米", "category": "穀物", "keywords": ["白", "粒"]},
        "bread": {"ja": "パン", "category": "穀物", "keywords": ["茶色", "ふわふわ"]},
        "flour": {"ja": "小麦粉", "category": "穀物", "keywords": ["白", "粉"]},
        "pasta": {"ja": "パスタ", "category": "麺類", "keywords": ["黄色", "長い"]},
        "udon": {"ja": "うどん", "category": "麺類", "keywords": ["白", "太い"]},
        "soba": {"ja": "そば", "category": "麺類", "keywords": ["茶色", "細い"]},
        "ramen": {"ja": "ラーメン", "category": "麺類", "keywords": ["黄色", "縮れ"]},
        # 豆類
        "tofu": {"ja": "豆腐", "category": "豆類", "keywords": ["白", "四角"]},
        "natto": {"ja": "納豆", "category": "豆類", "keywords": ["茶色", "粘る"]},
        "soybeans": {"ja": "大豆", "category": "豆類", "keywords": ["黄色", "丸い"]},
        "edamame": {"ja": "枝豆", "category": "豆類", "keywords": ["緑", "さや"]},
        # 調味料
        "soy_sauce": {"ja": "醤油", "category": "調味料", "keywords": ["茶色", "液体"]},
        "miso": {"ja": "味噌", "category": "調味料", "keywords": ["茶色", "ペースト"]},
        "sugar": {"ja": "砂糖", "category": "調味料", "keywords": ["白", "粒"]},
        "salt": {"ja": "塩", "category": "調味料", "keywords": ["白", "粒"]},
        "vinegar": {"ja": "酢", "category": "調味料", "keywords": ["透明", "液体"]},
        "sake": {"ja": "酒", "category": "調味料", "keywords": ["透明", "液体"]},
        "mirin": {"ja": "みりん", "category": "調味料", "keywords": ["透明", "液体"]},
        "oil": {"ja": "油", "category": "調味料", "keywords": ["黄色", "液体"]},
        "sesame_oil": {
            "ja": "ごま油",
            "category": "調味料",
            "keywords": ["茶色", "液体"],
        },
        # 果物
        "apple": {"ja": "りんご", "category": "果物", "keywords": ["赤", "丸い"]},
        "banana": {"ja": "バナナ", "category": "果物", "keywords": ["黄色", "長い"]},
        "orange": {
            "ja": "オレンジ",
            "category": "果物",
            "keywords": ["オレンジ", "丸い"],
        },
        "strawberry": {
            "ja": "いちご",
            "category": "果物",
            "keywords": ["赤", "小さい"],
        },
        "grape": {"ja": "ぶどう", "category": "果物", "keywords": ["紫", "房"]},
        "watermelon": {
            "ja": "スイカ",
            "category": "果物",
            "keywords": ["緑", "大きい"],
        },
        "peach": {"ja": "桃", "category": "果物", "keywords": ["ピンク", "丸い"]},
        "pear": {"ja": "梨", "category": "果物", "keywords": ["黄色", "洋梨"]},
        "kiwi": {"ja": "キウイ", "category": "果物", "keywords": ["茶色", "楕円"]},
        "lemon": {"ja": "レモン", "category": "果物", "keywords": ["黄色", "楕円"]},
        # その他
        "seaweed": {"ja": "海苔", "category": "海藻", "keywords": ["黒", "薄い"]},
        "wakame": {"ja": "わかめ", "category": "海藻", "keywords": ["緑", "薄い"]},
        "konbu": {"ja": "昆布", "category": "海藻", "keywords": ["黒", "厚い"]},
        "sesame": {"ja": "ごま", "category": "種実", "keywords": ["茶色", "小粒"]},
        "peanut": {"ja": "落花生", "category": "種実", "keywords": ["茶色", "小さい"]},
        "almond": {
            "ja": "アーモンド",
            "category": "種実",
            "keywords": ["茶色", "楕円"],
        },
        "walnut": {"ja": "くるみ", "category": "種実", "keywords": ["茶色", "凸凹"]},
        "chestnut": {"ja": "栗", "category": "種実", "keywords": ["茶色", "丸い"]},
        "sweet_potato": {
            "ja": "さつまいも",
            "category": "芋類",
            "keywords": ["紫", "長い"],
        },
        "taro": {"ja": "里芋", "category": "芋類", "keywords": ["茶色", "楕円"]},
        "corn": {"ja": "とうもろこし", "category": "野菜", "keywords": ["黄色", "粒"]},
        "pumpkin": {
            "ja": "かぼちゃ",
            "category": "野菜",
            "keywords": ["オレンジ", "大きい"],
        },
        "green_beans": {
            "ja": "いんげん",
            "category": "野菜",
            "keywords": ["緑", "細長い"],
        },
        "asparagus": {
            "ja": "アスパラガス",
            "category": "野菜",
            "keywords": ["緑", "細長い"],
        },
        "bamboo_shoot": {
            "ja": "たけのこ",
            "category": "野菜",
            "keywords": ["黄色", "円錐"],
        },
        "burdock": {"ja": "ごぼう", "category": "野菜", "keywords": ["茶色", "細長い"]},
        "lotus_root": {"ja": "れんこん", "category": "野菜", "keywords": ["白", "穴"]},
        "radish": {
            "ja": "ラディッシュ",
            "category": "野菜",
            "keywords": ["赤", "丸い"],
        },
        "zucchini": {
            "ja": "ズッキーニ",
            "category": "野菜",
            "keywords": ["緑", "長い"],
        },
        "celery": {"ja": "セロリ", "category": "野菜", "keywords": ["緑", "長い"]},
        "parsley": {"ja": "パセリ", "category": "野菜", "keywords": ["緑", "葉"]},
        "basil": {"ja": "バジル", "category": "野菜", "keywords": ["緑", "葉"]},
        "mint": {"ja": "ミント", "category": "野菜", "keywords": ["緑", "葉"]},
        "cilantro": {"ja": "パクチー", "category": "野菜", "keywords": ["緑", "葉"]},
        "bean_sprouts": {
            "ja": "もやし",
            "category": "野菜",
            "keywords": ["白", "細い"],
        },
        "okra": {"ja": "オクラ", "category": "野菜", "keywords": ["緑", "五角形"]},
        "bitter_melon": {
            "ja": "ゴーヤ",
            "category": "野菜",
            "keywords": ["緑", "凸凹"],
        },
    }

    def __init__(self, mode: str = "mock", cache_dir: Optional[Path] = None):
        """
        初期化

        Args:
          mode: 動作モード（'mock' または 'production'）
          cache_dir: キャッシュディレクトリ
        """
        self.mode = mode
        self.cache_dir = cache_dir or Path("data/cache/image_recognition")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ImageRecognitionService initialized in {mode} mode")

    def recognize_from_file(self, image_path: Path, max_results: int = 5) -> List[Dict]:
        """
        ファイルパスから画像認識

        Args:
          image_path: 画像ファイルパス
          max_results: 最大結果数

        Returns:
          認識結果リスト
        """
        try:
            with Image.open(image_path) as img:
                processed_img = self._preprocess_image(img)
                return self._recognize_image(processed_img, max_results)
        except Exception as e:
            logger.error(f"Failed to recognize image from file: {e}")
            raise

    def recognize_from_base64(
        self, base64_data: str, max_results: int = 5
    ) -> List[Dict]:
        """
        Base64エンコードされた画像から認識

        Args:
          base64_data: Base64エンコードされた画像データ
          max_results: 最大結果数

        Returns:
          認識結果リスト
        """
        try:
            # Base64デコード
            image_data = base64.b64decode(base64_data)
            img = Image.open(io.BytesIO(image_data))
            processed_img = self._preprocess_image(img)
            return self._recognize_image(processed_img, max_results)
        except Exception as e:
            logger.error(f"Failed to recognize image from base64: {e}")
            raise

    def recognize_from_url(self, image_url: str, max_results: int = 5) -> List[Dict]:
        """
        URL画像から認識（外部APIモード時のみ）

        Args:
          image_url: 画像URL
          max_results: 最大結果数

        Returns:
          認識結果リスト
        """
        if self.mode == "mock":
            logger.warning("URL recognition not supported in mock mode")
            return self._generate_mock_results(max_results)

        # 本番モード時は外部API呼び出し
        # TODO: 外部API統合実装
        logger.warning("Production mode URL recognition not yet implemented")
        return self._generate_mock_results(max_results)

    def _preprocess_image(self, img: Image.Image) -> Image.Image:
        """
        画像前処理（リサイズ、最適化）

        Args:
          img: 元画像

        Returns:
          前処理済み画像
        """
        # RGB変換
        if img.mode != "RGB":
            img = img.convert("RGB")

        # リサイズ（最大1024px）
        max_size = 1024
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        return img

    def _recognize_image(self, img: Image.Image, max_results: int = 5) -> List[Dict]:
        """
        画像認識実行

        Args:
          img: 前処理済み画像
          max_results: 最大結果数

        Returns:
          認識結果リスト
        """
        # キャッシュチェック
        cache_key = self._get_image_hash(img)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            logger.info(f"Cache hit for image hash: {cache_key}")
            return cached_result[:max_results]

        # モードに応じて認識処理
        if self.mode == "mock":
            results = self._generate_mock_results(max_results)
        else:
            results = self._call_external_api(img, max_results)

        # キャッシュ保存
        self._save_to_cache(cache_key, results)

        return results

    def _generate_mock_results(self, max_results: int = 5) -> List[Dict]:
        """
        モック結果生成（デモ用）

        Args:
          max_results: 最大結果数

        Returns:
          モック認識結果
        """
        import random

        # ランダムに食材を選択
        ingredients = random.sample(
            list(self.INGREDIENT_DICTIONARY.keys()), max_results
        )

        results = []
        for i, ingredient_id in enumerate(ingredients):
            info = self.INGREDIENT_DICTIONARY[ingredient_id]
            # 信頼度スコア（モック）
            confidence = round(0.95 - (i * 0.1), 2)

            results.append(
                {
                    "ingredient_id": ingredient_id,
                    "name": info["ja"],
                    "name_en": ingredient_id.replace("_", " ").title(),
                    "category": info["category"],
                    "confidence": confidence,
                    "keywords": info["keywords"],
                }
            )

        return results

    def _call_external_api(self, img: Image.Image, max_results: int = 5) -> List[Dict]:
        """
        外部AI API呼び出し（本番モード）

        Args:
          img: 画像
          max_results: 最大結果数

        Returns:
          認識結果
        """
        # External AI API integration placeholder
        # Supported APIs:
        # - OpenAI Vision API (GPT-4 Vision)
        # - Google Cloud Vision API
        # - AWS Rekognition
        # - Azure Computer Vision

        # TODO: Implement external API integration
        # Example implementation for OpenAI Vision:
        # import openai
        # response = openai.ChatCompletion.create(
        #     model="gpt-4-vision-preview",
        #     messages=[{
        #         "role": "user",
        #         "content": [
        #             {"type": "text", "text": "Identify food ingredients in this image"},
        #             {"type": "image_url", "image_url": {"url": img_base64}}
        #         ]
        #     }],
        #     max_tokens=300
        # )

        logger.warning("External API not yet implemented, using mock results")
        return self._generate_mock_results(max_results)

    def _get_image_hash(self, img: Image.Image) -> str:
        """
        画像のハッシュ値取得（キャッシュキー用）

        Args:
          img: 画像

        Returns:
          SHA256ハッシュ値
        """
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        return hashlib.sha256(img_bytes.getvalue()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[List[Dict]]:
        """
        キャッシュから結果取得

        Args:
          cache_key: キャッシュキー

        Returns:
          キャッシュされた結果（存在しない場合はNone）
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 有効期限チェック（24時間）
                cached_time = datetime.fromisoformat(data["timestamp"])
                if (datetime.now() - cached_time).total_seconds() > 86400:
                    return None
                return data["results"]
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return None

    def _save_to_cache(self, cache_key: str, results: List[Dict]) -> None:
        """
        結果をキャッシュに保存

        Args:
          cache_key: キャッシュキー
          results: 認識結果
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"timestamp": datetime.now().isoformat(), "results": results},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def get_ingredient_info(self, ingredient_id: str) -> Optional[Dict]:
        """
        食材情報取得

        Args:
          ingredient_id: 食材ID

        Returns:
          食材情報
        """
        if ingredient_id not in self.INGREDIENT_DICTIONARY:
            return None

        info = self.INGREDIENT_DICTIONARY[ingredient_id]
        return {
            "ingredient_id": ingredient_id,
            "name": info["ja"],
            "name_en": ingredient_id.replace("_", " ").title(),
            "category": info["category"],
            "keywords": info["keywords"],
        }

    def search_ingredients(
        self, query: str, category: Optional[str] = None
    ) -> List[Dict]:
        """
        食材検索

        Args:
          query: 検索クエリ
          category: カテゴリフィルター

        Returns:
          検索結果
        """
        results = []
        query_lower = query.lower()

        for ingredient_id, info in self.INGREDIENT_DICTIONARY.items():
            # カテゴリフィルター
            if category and info["category"] != category:
                continue

            # クエリマッチング
            if (
                query_lower in info["ja"].lower()
                or query_lower in ingredient_id.lower()
                or any(query_lower in kw.lower() for kw in info["keywords"])
            ):
                results.append(
                    {
                        "ingredient_id": ingredient_id,
                        "name": info["ja"],
                        "name_en": ingredient_id.replace("_", " ").title(),
                        "category": info["category"],
                        "keywords": info["keywords"],
                    }
                )

        return results

    def get_categories(self) -> List[str]:
        """
        カテゴリ一覧取得

        Returns:
          カテゴリリスト
        """
        categories = set(
            info["category"] for info in self.INGREDIENT_DICTIONARY.values()
        )
        return sorted(list(categories))


# シングルトンインスタンス
_image_recognition_service = None


def get_image_recognition_service(
    mode: str = "mock", cache_dir: Optional[Path] = None
) -> ImageRecognitionService:
    """画像認識サービス取得"""
    global _image_recognition_service
    if _image_recognition_service is None:
        _image_recognition_service = ImageRecognitionService(
            mode=mode, cache_dir=cache_dir
        )
    return _image_recognition_service
