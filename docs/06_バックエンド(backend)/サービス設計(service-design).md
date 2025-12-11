# サービス設計 (Service Design)

## 1. 概要

本ドキュメントは、Personal Recipe Intelligence (PRI) のバックエンドサービス層の設計を定義する。

## 2. サービス一覧

| サービス | 責務 |
|---------|------|
| RecipeService | レシピ CRUD 操作 |
| ScraperService | Web スクレイピング |
| OcrService | 画像テキスト抽出 |
| TranslateService | 翻訳処理 |
| CleanerService | データ正規化 |

## 3. サービス詳細

### 3.1 RecipeService

**責務**: レシピの CRUD 操作

```python
# services/recipe_service.py
from typing import Optional, List
from sqlmodel import Session, select
from backend.models.recipe import Recipe, RecipeIngredient, RecipeStep

class RecipeService:
    def __init__(self, session: Session):
        self.session = session

    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        sort: str = "created_at",
        order: str = "desc"
    ) -> tuple[List[Recipe], int]:
        """レシピ一覧取得"""
        statement = select(Recipe).where(Recipe.is_deleted == False)

        # ソート
        if order == "desc":
            statement = statement.order_by(getattr(Recipe, sort).desc())
        else:
            statement = statement.order_by(getattr(Recipe, sort))

        # カウント
        total = len(self.session.exec(statement).all())

        # ページネーション
        offset = (page - 1) * per_page
        statement = statement.offset(offset).limit(per_page)

        recipes = self.session.exec(statement).all()
        return recipes, total

    def get_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """レシピ詳細取得"""
        statement = select(Recipe).where(
            Recipe.id == recipe_id,
            Recipe.is_deleted == False
        )
        return self.session.exec(statement).first()

    def create(self, data: dict) -> Recipe:
        """レシピ作成"""
        # レシピ本体
        recipe = Recipe(
            title=data["title"],
            description=data.get("description"),
            servings=data.get("servings"),
            prep_time_minutes=data.get("prep_time_minutes"),
            cook_time_minutes=data.get("cook_time_minutes")
        )
        self.session.add(recipe)
        self.session.commit()
        self.session.refresh(recipe)

        # 材料
        for i, ing_data in enumerate(data.get("ingredients", [])):
            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                name=ing_data["name"],
                amount=ing_data.get("amount"),
                unit=ing_data.get("unit"),
                order_index=i
            )
            self.session.add(ingredient)

        # 手順
        for i, step_data in enumerate(data.get("steps", [])):
            step = RecipeStep(
                recipe_id=recipe.id,
                step_number=i + 1,
                description=step_data["description"]
            )
            self.session.add(step)

        self.session.commit()
        self.session.refresh(recipe)
        return recipe

    def update(self, recipe_id: int, data: dict) -> Optional[Recipe]:
        """レシピ更新"""
        recipe = self.get_by_id(recipe_id)
        if not recipe:
            return None

        for key, value in data.items():
            if hasattr(recipe, key) and value is not None:
                setattr(recipe, key, value)

        self.session.add(recipe)
        self.session.commit()
        self.session.refresh(recipe)
        return recipe

    def delete(self, recipe_id: int) -> bool:
        """レシピ削除（論理削除）"""
        recipe = self.get_by_id(recipe_id)
        if not recipe:
            return False

        recipe.is_deleted = True
        self.session.add(recipe)
        self.session.commit()
        return True

    def search(
        self,
        query: str = None,
        tag_ids: List[int] = None,
        ingredient: str = None
    ) -> List[Recipe]:
        """レシピ検索"""
        statement = select(Recipe).where(Recipe.is_deleted == False)

        if query:
            statement = statement.where(
                Recipe.title.contains(query) |
                Recipe.description.contains(query)
            )

        recipes = self.session.exec(statement).all()
        return recipes
```

### 3.2 ScraperService

**責務**: URL からレシピ情報を抽出

```python
# services/scraper_service.py
import httpx
from bs4 import BeautifulSoup
from typing import Optional
import json

class ScraperService:
    SUPPORTED_SITES = {
        "cookpad.com": "cookpad",
        "kurashiru.com": "kurashiru",
        "allrecipes.com": "allrecipes",
        "bbcgoodfood.com": "bbcgoodfood"
    }

    def __init__(self):
        self.client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; RecipeBot/1.0)"
            }
        )

    def scrape(self, url: str) -> dict:
        """URLからレシピを抽出"""
        # サイト判定
        site = self._detect_site(url)
        if not site:
            raise ValueError("対応していないサイトです")

        # robots.txt確認
        if not self._check_robots(url):
            raise PermissionError("robots.txtでブロックされています")

        # HTML取得
        response = self.client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # 構造化データ抽出試行
        recipe_data = self._extract_structured_data(soup)
        if not recipe_data:
            # DOMパーサーにフォールバック
            recipe_data = self._parse_by_site(soup, site)

        recipe_data["source_url"] = url
        recipe_data["source_site"] = site

        return recipe_data

    def _detect_site(self, url: str) -> Optional[str]:
        """サイト判定"""
        for domain, name in self.SUPPORTED_SITES.items():
            if domain in url:
                return name
        return None

    def _check_robots(self, url: str) -> bool:
        """robots.txt確認"""
        # 簡易実装
        return True

    def _extract_structured_data(self, soup: BeautifulSoup) -> Optional[dict]:
        """JSON-LD構造化データ抽出"""
        script_tags = soup.find_all("script", type="application/ld+json")

        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]
                if data.get("@type") == "Recipe":
                    return self._parse_structured_data(data)
            except:
                continue

        return None

    def _parse_structured_data(self, data: dict) -> dict:
        """構造化データをパース"""
        return {
            "title": data.get("name", ""),
            "description": data.get("description", ""),
            "servings": self._parse_servings(data.get("recipeYield")),
            "prep_time_minutes": self._parse_duration(data.get("prepTime")),
            "cook_time_minutes": self._parse_duration(data.get("cookTime")),
            "ingredients": data.get("recipeIngredient", []),
            "steps": self._parse_instructions(data.get("recipeInstructions", [])),
            "image_url": data.get("image", {}).get("url") if isinstance(data.get("image"), dict) else data.get("image")
        }

    def _parse_by_site(self, soup: BeautifulSoup, site: str) -> dict:
        """サイト別DOMパーサー"""
        parsers = {
            "cookpad": self._parse_cookpad,
            "allrecipes": self._parse_allrecipes,
        }

        parser = parsers.get(site)
        if parser:
            return parser(soup)

        raise ValueError(f"パーサーが未実装: {site}")

    def _parse_cookpad(self, soup: BeautifulSoup) -> dict:
        """クックパッド用パーサー"""
        title = soup.select_one("h1.recipe-title")
        ingredients = soup.select(".ingredient-list li")
        steps = soup.select(".step-list li")

        return {
            "title": title.text.strip() if title else "",
            "ingredients": [i.text.strip() for i in ingredients],
            "steps": [{"description": s.text.strip()} for s in steps]
        }

    def _parse_allrecipes(self, soup: BeautifulSoup) -> dict:
        """Allrecipes用パーサー"""
        title = soup.select_one("h1.article-heading")
        ingredients = soup.select(".mntl-structured-ingredients__list li")
        steps = soup.select(".recipe-instructions li")

        return {
            "title": title.text.strip() if title else "",
            "ingredients": [i.text.strip() for i in ingredients],
            "steps": [{"description": s.text.strip()} for s in steps]
        }

    def _parse_servings(self, value) -> Optional[int]:
        """分量パース"""
        if not value:
            return None
        if isinstance(value, int):
            return value
        import re
        match = re.search(r'\d+', str(value))
        return int(match.group()) if match else None

    def _parse_duration(self, value: str) -> Optional[int]:
        """ISO 8601期間をパース"""
        if not value:
            return None
        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', value)
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            return hours * 60 + minutes
        return None

    def _parse_instructions(self, instructions) -> list:
        """手順パース"""
        if isinstance(instructions, str):
            return [{"description": instructions}]
        if isinstance(instructions, list):
            return [
                {"description": i.get("text", i) if isinstance(i, dict) else str(i)}
                for i in instructions
            ]
        return []
```

### 3.3 OcrService

**責務**: 画像からテキスト抽出

```python
# services/ocr_service.py
import base64
from pathlib import Path
from typing import Optional
import httpx

class OcrService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def extract(self, image_path: str) -> dict:
        """画像からレシピテキストを抽出"""
        # 画像読み込み
        image_data = self._load_image(image_path)

        # Vision API呼び出し
        raw_text = self._call_vision_api(image_data)

        # 構造化
        structured = self._structure_text(raw_text)

        return {
            "raw_text": raw_text,
            **structured
        }

    def _load_image(self, image_path: str) -> str:
        """画像をBase64エンコード"""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"画像が見つかりません: {image_path}")

        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def _call_vision_api(self, image_data: str) -> str:
        """Vision APIでテキスト抽出"""
        # Claude Vision API呼び出し（実装例）
        # 実際の実装ではAPIキーと適切なエンドポイントを使用

        # ダミー実装
        return "抽出されたテキスト"

    def _structure_text(self, raw_text: str) -> dict:
        """テキストを構造化"""
        # 簡易実装
        lines = raw_text.strip().split("\n")

        title = lines[0] if lines else ""
        ingredients = []
        steps = []

        # 材料・手順の解析ロジック
        # ...

        return {
            "title": title,
            "ingredients": ingredients,
            "steps": steps
        }
```

### 3.4 TranslateService

**責務**: 翻訳処理

```python
# services/translate_service.py
import httpx
import hashlib
from typing import Optional
from sqlmodel import Session, select
from backend.models.translation_cache import TranslationCache

class TranslateService:
    DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"

    def __init__(self, session: Session, api_key: str):
        self.session = session
        self.api_key = api_key

    def translate(self, text: str, source_lang: str = "EN", target_lang: str = "JA") -> str:
        """テキストを翻訳"""
        if not text:
            return ""

        # キャッシュ確認
        cached = self._get_cache(text, source_lang, target_lang)
        if cached:
            return cached

        # API呼び出し
        translated = self._call_api(text, source_lang, target_lang)

        # キャッシュ保存
        self._save_cache(text, translated, source_lang, target_lang)

        return translated

    def translate_recipe(self, recipe_data: dict) -> dict:
        """レシピ全体を翻訳"""
        translated = recipe_data.copy()

        # タイトル
        if recipe_data.get("title"):
            translated["title_ja"] = self.translate(recipe_data["title"])

        # 説明
        if recipe_data.get("description"):
            translated["description_ja"] = self.translate(recipe_data["description"])

        # 材料
        if recipe_data.get("ingredients"):
            translated["ingredients"] = [
                {
                    **ing,
                    "name_ja": self.translate(ing.get("name", ing) if isinstance(ing, dict) else str(ing))
                }
                for ing in recipe_data["ingredients"]
            ]

        # 手順
        if recipe_data.get("steps"):
            translated["steps"] = [
                {
                    **step,
                    "description_ja": self.translate(step.get("description", ""))
                }
                for step in recipe_data["steps"]
            ]

        return translated

    def _get_cache(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """キャッシュ取得"""
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        statement = select(TranslationCache).where(
            TranslationCache.source_text_hash == text_hash,
            TranslationCache.source_lang == source_lang,
            TranslationCache.target_lang == target_lang
        )

        cache = self.session.exec(statement).first()
        return cache.translated_text if cache else None

    def _save_cache(self, source: str, translated: str, source_lang: str, target_lang: str):
        """キャッシュ保存"""
        text_hash = hashlib.sha256(source.encode()).hexdigest()

        cache = TranslationCache(
            source_text_hash=text_hash,
            source_text=source,
            translated_text=translated,
            source_lang=source_lang,
            target_lang=target_lang
        )

        self.session.add(cache)
        self.session.commit()

    def _call_api(self, text: str, source_lang: str, target_lang: str) -> str:
        """DeepL API呼び出し"""
        response = httpx.post(
            self.DEEPL_API_URL,
            data={
                "auth_key": self.api_key,
                "text": text,
                "source_lang": source_lang,
                "target_lang": target_lang
            }
        )
        response.raise_for_status()

        data = response.json()
        return data["translations"][0]["text"]
```

### 3.5 CleanerService

**責務**: データ正規化

```python
# services/cleaner_service.py
import re
from typing import List, Dict

class CleanerService:
    # 材料名正規化マップ
    INGREDIENT_NORMALIZATION = {
        "玉ねぎ": "たまねぎ",
        "玉葱": "たまねぎ",
        "タマネギ": "たまねぎ",
        "人参": "にんじん",
        "ニンジン": "にんじん",
        "大根": "だいこん",
        "ダイコン": "だいこん",
    }

    # 単位正規化マップ
    UNIT_NORMALIZATION = {
        "大さじ": "tbsp",
        "小さじ": "tsp",
        "カップ": "cup",
        "グラム": "g",
        "ミリリットル": "ml",
        "個": "個",
        "本": "本",
        "枚": "枚",
    }

    def clean_recipe(self, data: dict) -> dict:
        """レシピデータを正規化"""
        cleaned = data.copy()

        # タイトル正規化
        if cleaned.get("title"):
            cleaned["title"] = self._clean_text(cleaned["title"])

        # 材料正規化
        if cleaned.get("ingredients"):
            cleaned["ingredients"] = [
                self._clean_ingredient(ing)
                for ing in cleaned["ingredients"]
            ]

        # 手順正規化
        if cleaned.get("steps"):
            cleaned["steps"] = [
                self._clean_step(step)
                for step in cleaned["steps"]
            ]

        return cleaned

    def _clean_text(self, text: str) -> str:
        """テキスト正規化"""
        # 全角→半角変換
        text = text.translate(str.maketrans(
            "０１２３４５６７８９",
            "0123456789"
        ))

        # 余分な空白削除
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def _clean_ingredient(self, ingredient) -> dict:
        """材料正規化"""
        if isinstance(ingredient, str):
            # 文字列から解析
            parsed = self._parse_ingredient_string(ingredient)
        else:
            parsed = ingredient

        # 材料名正規化
        name = parsed.get("name", "")
        name_normalized = self.INGREDIENT_NORMALIZATION.get(name, name)
        name_normalized = self._to_hiragana(name_normalized)

        return {
            "name": name,
            "name_normalized": name_normalized,
            "amount": parsed.get("amount"),
            "unit": parsed.get("unit")
        }

    def _parse_ingredient_string(self, text: str) -> dict:
        """材料文字列をパース"""
        # 例: "たまねぎ 2個" -> {"name": "たまねぎ", "amount": 2, "unit": "個"}

        pattern = r'^(.+?)\s*(\d+(?:\.\d+)?|½|⅓|¼)?\s*(.+)?$'
        match = re.match(pattern, text.strip())

        if match:
            name = match.group(1).strip()
            amount_str = match.group(2)
            unit = match.group(3).strip() if match.group(3) else None

            # 分数変換
            amount = self._parse_fraction(amount_str) if amount_str else None

            return {"name": name, "amount": amount, "unit": unit}

        return {"name": text, "amount": None, "unit": None}

    def _parse_fraction(self, value: str) -> float:
        """分数をパース"""
        fractions = {"½": 0.5, "⅓": 0.333, "¼": 0.25, "¾": 0.75}
        if value in fractions:
            return fractions[value]
        try:
            return float(value)
        except:
            return None

    def _to_hiragana(self, text: str) -> str:
        """カタカナ→ひらがな変換"""
        return "".join(
            chr(ord(c) - 0x60) if 'ァ' <= c <= 'ン' else c
            for c in text
        )

    def _clean_step(self, step) -> dict:
        """手順正規化"""
        if isinstance(step, str):
            description = step
        else:
            description = step.get("description", "")

        description = self._clean_text(description)

        return {"description": description}
```

## 4. 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2024-12-11 | 1.0.0 | 初版作成 |
