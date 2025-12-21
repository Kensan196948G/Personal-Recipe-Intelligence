"""
CSV Import Service - レシピのCSVインポート機能
"""

import csv
import io
from typing import Optional

from sqlmodel import Session

from backend.models.recipe import Ingredient, Recipe, RecipeTag, Step, Tag
from backend.services.normalizer import IngredientNormalizer

# 材料名正規化用のインスタンスを作成
_normalizer = None


def get_normalizer() -> IngredientNormalizer:
    global _normalizer
    if _normalizer is None:
        _normalizer = IngredientNormalizer()
    return _normalizer


def normalize_ingredient_name(name: str) -> str:
    """材料名を正規化する"""
    return get_normalizer().normalize_ingredient_name(name)


class CSVImportService:
    """CSVインポートサービス"""

    # サポートするCSVフォーマット
    REQUIRED_COLUMNS = ["title"]
    OPTIONAL_COLUMNS = [
        "description",
        "servings",
        "prep_time_minutes",
        "cook_time_minutes",
        "source_url",
        "source_type",
        "ingredients",
        "steps",
        "tags",
    ]

    # 日本語ヘッダーから英語ヘッダーへのマッピング
    HEADER_MAPPING = {
        "タイトル": "title",
        "説明": "description",
        "人数": "servings",
        "準備時間（分）": "prep_time_minutes",
        "調理時間（分）": "cook_time_minutes",
        "URL": "source_url",
        "ソース種別": "source_type",
        "材料": "ingredients",
        "手順": "steps",
        "タグ": "tags",
    }

    def __init__(self, session: Session):
        self.session = session

    def _normalize_headers(self, row: dict) -> dict:
        """日本語ヘッダーを英語ヘッダーに変換"""
        normalized = {}
        for key, value in row.items():
            # 日本語ヘッダーの場合は英語に変換
            normalized_key = self.HEADER_MAPPING.get(key, key)
            normalized[normalized_key] = value
        return normalized

    def parse_csv(self, csv_content: str) -> list[dict]:
        """CSVコンテンツをパースしてレシピデータのリストを返す"""
        recipes = []
        errors = []

        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            headers = reader.fieldnames or []

            # ヘッダーを正規化（日本語→英語）
            normalized_headers = [
                self.HEADER_MAPPING.get(h, h) for h in headers
            ]

            # 必須カラムのチェック（日本語・英語両方対応）
            missing_columns = [
                col for col in self.REQUIRED_COLUMNS if col not in normalized_headers
            ]
            if missing_columns:
                raise ValueError(f"必須カラムがありません: {', '.join(missing_columns)}（「タイトル」または「title」）")

            for row_num, row in enumerate(reader, start=2):
                try:
                    # 日本語ヘッダーを英語に変換
                    normalized_row = self._normalize_headers(row)
                    recipe_data = self._parse_row(normalized_row)
                    recipes.append(recipe_data)
                except ValueError as e:
                    errors.append({"row": row_num, "error": str(e)})

        except csv.Error as e:
            raise ValueError(f"CSV解析エラー: {str(e)}")

        return {"recipes": recipes, "errors": errors}

    def _parse_row(self, row: dict) -> dict:
        """CSVの1行をパースしてレシピデータに変換"""
        title = row.get("title", "").strip()
        if not title:
            raise ValueError("タイトルは必須です")

        recipe_data = {
            "title": title,
            "description": row.get("description", "").strip() or None,
            "servings": self._parse_int(row.get("servings")),
            "prep_time_minutes": self._parse_int(row.get("prep_time_minutes")),
            "cook_time_minutes": self._parse_int(row.get("cook_time_minutes")),
            "source_url": row.get("source_url", "").strip() or None,
            "source_type": row.get("source_type", "csv").strip() or "csv",
            "ingredients": self._parse_ingredients(row.get("ingredients", "")),
            "steps": self._parse_steps(row.get("steps", "")),
            "tags": self._parse_tags(row.get("tags", "")),
        }

        return recipe_data

    def _parse_int(self, value: Optional[str]) -> Optional[int]:
        """文字列を整数に変換"""
        if not value:
            return None
        try:
            return int(value.strip())
        except ValueError:
            return None

    def _parse_ingredients(self, value: str) -> list[dict]:
        """材料文字列をパース
        フォーマット: "材料名:量:単位|材料名:量:単位" または "材料名 量単位, 材料名 量単位"
        """
        if not value or not value.strip():
            return []

        ingredients = []
        # パイプ区切りの場合
        if "|" in value:
            items = value.split("|")
        # カンマ区切りの場合
        elif "," in value:
            items = value.split(",")
        # 改行区切りの場合
        elif "\n" in value:
            items = value.split("\n")
        else:
            items = [value]

        for order, item in enumerate(items, start=1):
            item = item.strip()
            if not item:
                continue

            # コロン区切りの場合: "材料名:量:単位"
            if ":" in item:
                parts = item.split(":")
                name = parts[0].strip()
                amount = self._parse_float(parts[1]) if len(parts) > 1 else None
                unit = parts[2].strip() if len(parts) > 2 else None
            else:
                # スペース区切りで解析: "材料名 100g"
                name, amount, unit = self._parse_ingredient_text(item)

            if name:
                ingredients.append(
                    {
                        "name": name,
                        "name_normalized": normalize_ingredient_name(name),
                        "amount": amount,
                        "unit": unit,
                        "order": order,
                    }
                )

        return ingredients

    def _parse_ingredient_text(self, text: str) -> tuple:
        """材料テキストを解析して名前、量、単位を抽出"""
        import re

        text = text.strip()

        # "材料名 100g" や "材料名 1個" のパターン
        match = re.match(r"^(.+?)\s+(\d+(?:\.\d+)?)\s*(\S*)$", text)
        if match:
            name = match.group(1).strip()
            amount = self._parse_float(match.group(2))
            unit = match.group(3).strip() or None
            return name, amount, unit

        # 数字が含まれていない場合は名前のみ
        return text, None, None

    def _parse_float(self, value: Optional[str]) -> Optional[float]:
        """文字列を浮動小数点数に変換"""
        if not value:
            return None
        try:
            return float(value.strip())
        except ValueError:
            return None

    def _parse_steps(self, value: str) -> list[dict]:
        """調理手順文字列をパース
        フォーマット: "手順1|手順2|手順3" または "1. 手順1 2. 手順2"
        """
        if not value or not value.strip():
            return []

        steps = []
        # パイプ区切りの場合
        if "|" in value:
            items = value.split("|")
        # 改行区切りの場合
        elif "\n" in value:
            items = value.split("\n")
        else:
            # 番号付きの場合: "1. 手順 2. 手順"
            import re

            items = re.split(r"\d+\.\s*", value)

        for order, item in enumerate(items, start=1):
            item = item.strip()
            if item:
                steps.append({"description": item, "order": order})

        return steps

    def _parse_tags(self, value: str) -> list[str]:
        """タグ文字列をパース
        フォーマット: "タグ1,タグ2,タグ3" または "タグ1|タグ2|タグ3"
        """
        if not value or not value.strip():
            return []

        # パイプまたはカンマで分割
        if "|" in value:
            items = value.split("|")
        else:
            items = value.split(",")

        return [item.strip() for item in items if item.strip()]

    def import_recipes(
        self, csv_content: str, skip_duplicates: bool = True
    ) -> dict:
        """CSVからレシピをインポート"""
        result = self.parse_csv(csv_content)
        recipes_data = result["recipes"]
        parse_errors = result["errors"]

        imported = []
        skipped = []
        import_errors = []

        for idx, recipe_data in enumerate(recipes_data):
            try:
                # 重複チェック
                if skip_duplicates:
                    existing = (
                        self.session.query(Recipe)
                        .filter(Recipe.title == recipe_data["title"])
                        .first()
                    )
                    if existing:
                        skipped.append(
                            {
                                "title": recipe_data["title"],
                                "reason": "duplicate",
                            }
                        )
                        continue

                # レシピ作成
                recipe = self._create_recipe(recipe_data)
                imported.append({"id": recipe.id, "title": recipe.title})

            except Exception as e:
                import_errors.append(
                    {"title": recipe_data.get("title", f"Row {idx}"), "error": str(e)}
                )

        return {
            "imported": imported,
            "skipped": skipped,
            "errors": parse_errors + import_errors,
            "summary": {
                "total": len(recipes_data),
                "imported": len(imported),
                "skipped": len(skipped),
                "errors": len(parse_errors) + len(import_errors),
            },
        }

    def _create_recipe(self, recipe_data: dict) -> Recipe:
        """レシピをデータベースに作成"""
        # レシピ本体を作成
        recipe = Recipe(
            title=recipe_data["title"],
            description=recipe_data.get("description"),
            servings=recipe_data.get("servings"),
            prep_time_minutes=recipe_data.get("prep_time_minutes"),
            cook_time_minutes=recipe_data.get("cook_time_minutes"),
            source_url=recipe_data.get("source_url"),
            source_type=recipe_data.get("source_type", "csv"),
        )
        self.session.add(recipe)
        self.session.flush()  # IDを取得するため

        # 材料を追加
        for ing_data in recipe_data.get("ingredients", []):
            ingredient = Ingredient(
                recipe_id=recipe.id,
                name=ing_data["name"],
                name_normalized=ing_data.get(
                    "name_normalized", normalize_ingredient_name(ing_data["name"])
                ),
                amount=ing_data.get("amount"),
                unit=ing_data.get("unit"),
                order=ing_data.get("order", 0),
            )
            self.session.add(ingredient)

        # 手順を追加
        for step_data in recipe_data.get("steps", []):
            step = Step(
                recipe_id=recipe.id,
                description=step_data["description"],
                order=step_data.get("order", 1),
            )
            self.session.add(step)

        # タグを追加
        for tag_name in recipe_data.get("tags", []):
            # 既存タグを検索または作成
            tag = self.session.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                self.session.add(tag)
                self.session.flush()

            recipe_tag = RecipeTag(recipe_id=recipe.id, tag_id=tag.id)
            self.session.add(recipe_tag)

        self.session.commit()
        return recipe

    def get_sample_csv(self) -> str:
        """サンプルCSVを生成"""
        output = io.StringIO()
        writer = csv.writer(output)

        # ヘッダー（日本語）
        headers = [
            "タイトル",
            "説明",
            "人数",
            "準備時間（分）",
            "調理時間（分）",
            "URL",
            "ソース種別",
            "材料",
            "手順",
            "タグ",
        ]
        writer.writerow(headers)

        # サンプルデータ
        sample_rows = [
            [
                "カレーライス",
                "家庭の定番カレー。野菜たっぷりで栄養満点",
                "4",
                "20",
                "40",
                "",
                "manual",
                "たまねぎ:2:個|にんじん:1:本|じゃがいも:3:個|豚肉:300:g|カレールー:1:箱|水:800:ml",
                "野菜を一口大に切る|肉を炒めて取り出す|野菜を炒める|水を加えて20分煮込む|ルーを入れて10分煮込む",
                "和食,定番,簡単,メイン",
            ],
            [
                "味噌汁",
                "毎日飲みたい基本の味噌汁",
                "2",
                "5",
                "10",
                "",
                "manual",
                "豆腐:1:丁|わかめ:5:g|味噌:大さじ2|だし汁:400:ml|ねぎ:適量",
                "だし汁を温める|豆腐を切って入れる|わかめを入れる|味噌を溶かす|ねぎを散らす",
                "和食,汁物,朝食,ヘルシー",
            ],
            [
                "肉じゃが",
                "ほっこり美味しい家庭料理の定番",
                "4",
                "15",
                "30",
                "",
                "manual",
                "牛肉:200:g|じゃがいも:4:個|たまねぎ:1:個|にんじん:1:本|しらたき:1:袋|醤油:大さじ3|みりん:大さじ2|砂糖:大さじ1|だし汁:300:ml",
                "材料を一口大に切る|牛肉を炒める|野菜を加えて炒める|調味料とだし汁を加える|落とし蓋をして20分煮込む",
                "和食,定番,煮物,メイン",
            ],
            [
                "親子丼",
                "とろとろ卵がたまらない定番丼",
                "2",
                "10",
                "15",
                "",
                "manual",
                "鶏もも肉:200:g|たまねぎ:1:個|卵:3:個|醤油:大さじ2|みりん:大さじ2|だし汁:100:ml|ご飯:2:膳|三つ葉:適量",
                "鶏肉を一口大に切る|たまねぎを薄切りにする|調味料とだし汁を煮立てる|鶏肉とたまねぎを入れて煮る|溶き卵を回し入れる|半熟で火を止めご飯にのせる",
                "和食,丼物,簡単,メイン",
            ],
            [
                "豚の生姜焼き",
                "ご飯がすすむ定番おかず",
                "2",
                "10",
                "10",
                "",
                "manual",
                "豚ロース:300:g|生姜:1:かけ|醤油:大さじ2|みりん:大さじ1|酒:大さじ1|キャベツ:適量",
                "生姜をすりおろす|調味料を混ぜる|豚肉を焼く|タレを加えて絡める|キャベツと盛り付ける",
                "和食,定番,簡単,メイン,お弁当",
            ],
            [
                "ハンバーグ",
                "ジューシーな手作りハンバーグ",
                "4",
                "20",
                "20",
                "",
                "manual",
                "合い挽き肉:400:g|たまねぎ:1:個|パン粉:1/2:カップ|牛乳:50:ml|卵:1:個|塩:小さじ1|こしょう:少々|ナツメグ:少々",
                "たまねぎをみじん切りにして炒める|パン粉を牛乳に浸す|材料をすべて混ぜてこねる|形を整えて中央をくぼませる|両面を焼いて蓋をして蒸し焼きにする",
                "洋食,定番,メイン,子供向け",
            ],
            [
                "チャーハン",
                "パラパラ仕上げの基本チャーハン",
                "2",
                "5",
                "10",
                "",
                "manual",
                "ご飯:2:膳|卵:2:個|ねぎ:1/2:本|チャーシュー:50:g|塩:少々|こしょう:少々|醤油:小さじ1|ごま油:大さじ1",
                "具材を細かく切る|強火で卵を炒める|ご飯を加えてほぐしながら炒める|具材を加える|調味料で味を整える",
                "中華,簡単,定番,メイン,お昼",
            ],
            [
                "野菜炒め",
                "シャキシャキ野菜の簡単炒め物",
                "2",
                "10",
                "5",
                "",
                "manual",
                "キャベツ:1/4:個|にんじん:1/2:本|もやし:1:袋|豚肉:100:g|塩:少々|こしょう:少々|醤油:小さじ1|ごま油:大さじ1",
                "野菜を切る|強火で豚肉を炒める|固い野菜から順に炒める|調味料で味を整える",
                "中華,簡単,ヘルシー,副菜",
            ],
            [
                "オムライス",
                "ふわとろ卵のオムライス",
                "2",
                "15",
                "15",
                "",
                "manual",
                "ご飯:2:膳|鶏肉:100:g|たまねぎ:1/2:個|ケチャップ:大さじ4|卵:4:個|バター:20:g|塩:少々|こしょう:少々",
                "鶏肉とたまねぎを炒める|ご飯を加えてケチャップで味付け|別のフライパンでバターを溶かす|溶き卵を入れて半熟で包む|ケチャップをかける",
                "洋食,定番,メイン,子供向け",
            ],
            [
                "ポテトサラダ",
                "クリーミーで美味しいポテトサラダ",
                "4",
                "15",
                "15",
                "",
                "manual",
                "じゃがいも:4:個|きゅうり:1:本|にんじん:1/2:本|ハム:4:枚|マヨネーズ:大さじ4|塩:少々|こしょう:少々|酢:小さじ1",
                "じゃがいもを茹でてつぶす|きゅうりとにんじんを薄切りにして塩もみする|ハムを切る|熱いうちに酢を加える|冷めてからマヨネーズと具材を混ぜる",
                "洋食,副菜,サラダ,お弁当",
            ],
        ]
        for row in sample_rows:
            writer.writerow(row)

        return output.getvalue()
