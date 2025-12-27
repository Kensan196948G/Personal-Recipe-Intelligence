"""
エクスポート強化サービス

複数フォーマット対応、レシピブック生成、買い物リスト、栄養レポート等のエクスポート機能を提供
"""

import csv
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.dom import minidom

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class ExportEnhancedService:
    """エクスポート強化サービス"""

    SUPPORTED_FORMATS = {
        "json": {"name": "JSON", "mime": "application/json", "ext": ".json"},
        "csv": {"name": "CSV", "mime": "text/csv", "ext": ".csv"},
        "xml": {"name": "XML (RecipeML)", "mime": "application/xml", "ext": ".xml"},
        "markdown": {"name": "Markdown", "mime": "text/markdown", "ext": ".md"},
        "pdf": {"name": "PDF", "mime": "application/pdf", "ext": ".pdf"},
    }

    # カテゴリー別アイコンマッピング
    CATEGORY_ICONS = {
        "和食": "🍱",
        "洋食": "🍝",
        "中華": "🥟",
        "イタリアン": "🇮🇹",
        "フレンチ": "🇫🇷",
        "メキシカン": "🌮",
        "韓国料理": "🇰🇷",
        "タイ料理": "🇹🇭",
        "インド料理": "🇮🇳",
        "メインディッシュ": "🍖",
        "スープ": "🍲",
        "サラダ": "🥗",
        "デザート": "🍰",
        "パスタ": "🍝",
        "カレー": "🍛",
        "丼": "🍚",
        "麺": "🍜",
        "パン": "🍞",
        "ごはん": "🍚",
        "default": "🍽️"
    }

    # 材料別アイコンマッピング（日本語・英語対応、100種類以上）
    INGREDIENT_ICONS = {
        # 肉類（日本語）
        "肉": "🥩", "牛肉": "🥩", "豚肉": "🥓", "鶏肉": "🍗", "挽き肉": "🍖",
        "合挽き肉": "🍖", "牛豚合挽き肉": "🍖", "ひき肉": "🍖",
        "ハム": "🥓", "ベーコン": "🥓", "ソーセージ": "🌭",
        "鴨": "🦆", "ラム": "🍖", "羊肉": "🍖",
        # 肉類（英語）
        "beef": "🥩", "pork": "🥓", "chicken": "🍗", "meat": "🥩",
        "ground": "🍖", "ham": "🥓", "bacon": "🥓", "sausage": "🌭",
        # 魚介類（日本語）
        "魚": "🐟", "鮭": "🐟", "サーモン": "🐟", "マグロ": "🐟", "サバ": "🐟",
        "エビ": "🦐", "海老": "🦐", "イカ": "🦑", "タコ": "🐙",
        "貝": "🦪", "カニ": "🦀", "蟹": "🦀", "ホタテ": "🦪",
        # 魚介類（英語）
        "fish": "🐟", "salmon": "🐟", "tuna": "🐟", "shrimp": "🦐",
        "squid": "🦑", "octopus": "🐙", "crab": "🦀", "shellfish": "🦪",
        # 野菜（日本語）
        "野菜": "🥬", "玉ねぎ": "🧅", "玉葱": "🧅", "タマネギ": "🧅",
        "トマト": "🍅", "ミニトマト": "🍅", "プチトマト": "🍅",
        "人参": "🥕", "にんじん": "🥕", "ニンジン": "🥕", "キャロット": "🥕",
        "じゃがいも": "🥔", "ジャガイモ": "🥔", "馬鈴薯": "🥔",
        "ブロッコリー": "🥦", "きゅうり": "🥒", "胡瓜": "🥒",
        "なす": "🍆", "茄子": "🍆", "ナス": "🍆",
        "レタス": "🥬", "キャベツ": "🥬", "ほうれん草": "🥬", "白菜": "🥬",
        "ピーマン": "🫑", "パプリカ": "🫑", "唐辛子": "🌶️",
        "大根": "🥬", "かぶ": "🥬", "ごぼう": "🥬", "れんこん": "🥬",
        "ネギ": "🧅", "長ネギ": "🧅", "葱": "🧅", "ニラ": "🥬",
        "わかめ": "🥬", "海藻": "🥬", "昆布": "🥬", "のり": "🥬",
        # 野菜（英語）
        "onion": "🧅", "tomato": "🍅", "carrot": "🥕", "potato": "🥔",
        "broccoli": "🥦", "cucumber": "🥒", "eggplant": "🍆",
        "lettuce": "🥬", "cabbage": "🥬", "spinach": "🥬",
        "pepper": "🫑", "bell pepper": "🫑", "chili": "🌶️",
        # きのこ・豆類
        "きのこ": "🍄", "しめじ": "🍄", "えのき": "🍄", "舞茸": "🍄", "椎茸": "🍄",
        "豆": "🫘", "枝豆": "🫛", "大豆": "🫘", "小豆": "🫘",
        "豆腐": "🧊", "厚揚げ": "🧊", "油揚げ": "🧊", "納豆": "🫘",
        "mushroom": "🍄", "bean": "🫘", "tofu": "🧊",
        # 卵・乳製品
        "卵": "🥚", "たまご": "🥚", "玉子": "🥚", "egg": "🥚",
        "チーズ": "🧀", "cheese": "🧀", "バター": "🧈", "butter": "🧈",
        "牛乳": "🥛", "ミルク": "🥛", "milk": "🥛",
        "ヨーグルト": "🥛", "yogurt": "🥛", "生クリーム": "🥛", "cream": "🥛",
        # 穀物・麺・米
        "米": "🌾", "ご飯": "🍚", "白米": "🍚", "玄米": "🍚", "rice": "🍚",
        "パン": "🍞", "食パン": "🍞", "bread": "🍞", "パン粉": "🍞",
        "パスタ": "🍝", "スパゲッティ": "🍝", "pasta": "🍝", "spaghetti": "🍝",
        "麺": "🍜", "うどん": "🍜", "そば": "🍜", "ラーメン": "🍜",
        "noodle": "🍜", "udon": "🍜", "soba": "🍜", "ramen": "🍜",
        "小麦粉": "🌾", "flour": "🌾", "片栗粉": "🌾",
        # 調味料・香辛料
        "塩": "🧂", "砂糖": "🧂", "salt": "🧂", "sugar": "🧂",
        "醤油": "🫙", "しょうゆ": "🫙", "soy sauce": "🫙",
        "味噌": "🫙", "みそ": "🫙", "miso": "🫙",
        "油": "🫙", "サラダ油": "🫙", "ごま油": "🫙", "オリーブオイル": "🫒", "olive oil": "🫒",
        "酢": "🫙", "vinegar": "🫙", "みりん": "🫙", "酒": "🫙", "sake": "🫙",
        "ケチャップ": "🍅", "ketchup": "🍅", "マヨネーズ": "🥚", "mayonnaise": "🥚",
        "ソース": "🫙", "sauce": "🫙", "ドレッシング": "🫙", "dressing": "🫙",
        "だし": "🍲", "出汁": "🍲", "コンソメ": "🍲", "ブイヨン": "🍲", "stock": "🍲",
        "カレールー": "🍛", "curry": "🍛",
        # ハーブ・スパイス
        "ニンニク": "🧄", "にんにく": "🧄", "garlic": "🧄",
        "生姜": "🫚", "しょうが": "🫚", "ショウガ": "🫚", "ginger": "🫚",
        "バジル": "🌿", "basil": "🌿", "パセリ": "🌿", "parsley": "🌿",
        "ローズマリー": "🌿", "rosemary": "🌿", "タイム": "🌿", "thyme": "🌿",
        "コショウ": "🧂", "胡椒": "🧂", "pepper": "🧂",
        "唐辛子": "🌶️", "チリ": "🌶️", "chili": "🌶️",
        # 果物
        "レモン": "🍋", "lemon": "🍋", "ライム": "🍋", "lime": "🍋",
        "りんご": "🍎", "apple": "🍎", "バナナ": "🍌", "banana": "🍌",
        "オレンジ": "🍊", "orange": "🍊", "桃": "🍑", "peach": "🍑",
        "いちご": "🍓", "strawberry": "🍓", "ブルーベリー": "🫐", "blueberry": "🫐",
        # その他
        "水": "💧", "water": "💧", "氷": "🧊", "ice": "🧊",
        "ワイン": "🍷", "wine": "🍷", "ビール": "🍺", "beer": "🍺",
        "ナッツ": "🥜", "nuts": "🥜", "アーモンド": "🥜", "almond": "🥜",
        "はちみつ": "🍯", "蜂蜜": "🍯", "honey": "🍯",
        "チョコレート": "🍫", "chocolate": "🍫",
        "default": "🔸"
    }

    # タグ別アイコンマッピング（拡充版）
    TAG_ICONS = {
        # ジャンル
        "和食": "🍱", "洋食": "🍝", "中華": "🥟", "イタリアン": "🇮🇹",
        "フレンチ": "🇫🇷", "メキシカン": "🌮", "韓国料理": "🇰🇷",
        "タイ料理": "🇹🇭", "インド料理": "🇮🇳", "アジアン": "🥢",
        # 難易度・特徴
        "簡単": "⭐", "時短": "⚡", "人気": "❤️", "定番": "👍",
        "本格": "👨‍🍳", "プロ": "👨‍🍳", "初心者": "🔰",
        # 健康・ダイエット
        "ヘルシー": "🌱", "低カロリー": "💪", "高タンパク": "💪",
        "ベジタリアン": "🥗", "ビーガン": "🌿", "グルテンフリー": "🌾",
        # 料理種別
        "メイン": "🍖", "主菜": "🍖", "副菜": "🥗", "おかず": "🍱",
        "汁物": "🍲", "スープ": "🍲", "サラダ": "🥗",
        "デザート": "🍰", "スイーツ": "🧁", "お菓子": "🍪",
        # 調理方法
        "焼く": "🔥", "煮る": "🍲", "炒める": "🍳", "揚げる": "🍤",
        "蒸す": "♨️", "茹でる": "💧", "グリル": "🔥", "オーブン": "🔥",
        # 食材分類
        "肉料理": "🥩", "魚料理": "🐟", "野菜料理": "🥬", "卵料理": "🥚",
        "豆腐料理": "🧊", "麺料理": "🍜", "ご飯": "🍚", "パン": "🍞",
        # 季節・イベント
        "春": "🌸", "夏": "☀️", "秋": "🍂", "冬": "❄️",
        "クリスマス": "🎄", "正月": "🎍", "ハロウィン": "🎃",
        # その他
        "作り置き": "📦", "お弁当": "🍱", "おつまみ": "🍻",
        "朝食": "🌅", "昼食": "☀️", "夕食": "🌙", "夜食": "🌙",
        "子供向け": "👶", "大人向け": "👨", "パーティー": "🎉",
        "default": "🏷️"
    }

    def __init__(self, data_dir: str = "data"):
        """
        初期化

        Args:
            data_dir: データディレクトリパス
        """
        self.data_dir = Path(data_dir)
        self.exports_dir = self.data_dir / "exports"
        self.backups_dir = self.data_dir / "backups"
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)

        # 日本語フォント登録（Noto Sans JP または IPAゴシック）
        self._register_japanese_font()

    def _get_category_icon(self, category: Optional[str]) -> str:
        """カテゴリーに応じたアイコンを取得"""
        if not category:
            return self.CATEGORY_ICONS["default"]
        return self.CATEGORY_ICONS.get(category, self.CATEGORY_ICONS["default"])

    def _get_ingredient_icon(self, ingredient_name: str) -> str:
        """材料名に応じたアイコンを取得（長いキーワード優先）"""
        if not ingredient_name:
            return self.INGREDIENT_ICONS["default"]

        # 長いキーワードから優先的にマッチング（より具体的な材料名を優先）
        sorted_keywords = sorted(
            self.INGREDIENT_ICONS.items(), key=lambda x: len(x[0]), reverse=True
        )

        for keyword, icon in sorted_keywords:
            if keyword != "default" and keyword in ingredient_name:
                return icon
        return self.INGREDIENT_ICONS["default"]

    def _get_tag_icon(self, tag_name: str) -> str:
        """タグに応じたアイコンを取得"""
        if not tag_name:
            return self.TAG_ICONS["default"]
        return self.TAG_ICONS.get(tag_name, self.TAG_ICONS["default"])

    def _register_japanese_font(self) -> None:
        """日本語フォントを登録"""
        try:
            # システムにインストールされているフォントを探す
            font_paths = [
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
                "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
            ]

            for font_path in font_paths:
                if Path(font_path).exists():
                    pdfmetrics.registerFont(TTFont("Japanese", font_path))
                    return

            # フォントが見つからない場合はデフォルトフォント使用
            print("Warning: Japanese font not found. Using default font.")
        except Exception as e:
            print(f"Warning: Failed to register Japanese font: {e}")

    def get_supported_formats(self) -> Dict[str, Dict[str, str]]:
        """
        対応フォーマット一覧を取得

        Returns:
            フォーマット情報の辞書
        """
        return self.SUPPORTED_FORMATS

    def export_recipes(
        self,
        recipes: List[Dict[str, Any]],
        format_type: str = "json",
        options: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """
        レシピをエクスポート

        Args:
            recipes: レシピリスト
            format_type: エクスポートフォーマット
            options: オプション設定

        Returns:
            エクスポートデータ（バイト列）

        Raises:
            ValueError: 未対応のフォーマット
        """
        if format_type not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format_type}")

        options = options or {}

        if format_type == "json":
            return self._export_json(recipes, options)
        elif format_type == "csv":
            return self._export_csv(recipes, options)
        elif format_type == "xml":
            return self._export_xml(recipes, options)
        elif format_type == "markdown":
            return self._export_markdown(recipes, options)
        elif format_type == "pdf":
            return self._export_pdf(recipes, options)

        raise ValueError(f"Format not implemented: {format_type}")

    def _export_json(
        self, recipes: List[Dict[str, Any]], options: Dict[str, Any]
    ) -> bytes:
        """JSON形式でエクスポート"""
        indent = options.get("indent", 2)
        ensure_ascii = options.get("ensure_ascii", False)

        data = {
            "exported_at": datetime.now().isoformat(),
            "format_version": "1.0",
            "recipe_count": len(recipes),
            "recipes": recipes,
        }

        json_str = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
        return json_str.encode("utf-8")

    def _export_csv(
        self, recipes: List[Dict[str, Any]], options: Dict[str, Any]
    ) -> bytes:
        """CSV形式でエクスポート（Excel互換）"""
        output = StringIO()
        writer = csv.writer(output)

        # ヘッダー
        headers = [
            "ID",
            "タイトル",
            "説明",
            "調理時間（分）",
            "人数",
            "カテゴリー",
            "タグ",
            "材料",
            "手順",
            "作成日",
        ]
        writer.writerow(headers)

        # データ行
        for recipe in recipes:
            ingredients = "; ".join(
                [
                    f"{ing.get('name', '')} {ing.get('amount', '')} {ing.get('unit', '')}"
                    for ing in recipe.get("ingredients", [])
                ]
            )
            steps = "; ".join(recipe.get("steps", []))
            tags = ", ".join(recipe.get("tags", []))

            row = [
                recipe.get("id", ""),
                recipe.get("title", ""),
                recipe.get("description", ""),
                recipe.get("cooking_time_minutes", ""),
                recipe.get("servings", ""),
                recipe.get("category", ""),
                tags,
                ingredients,
                steps,
                recipe.get("created_at", ""),
            ]
            writer.writerow(row)

        # BOM付きUTF-8でエンコード（Excel互換）
        csv_content = output.getvalue()
        return b"\xef\xbb\xbf" + csv_content.encode("utf-8")

    def _export_xml(
        self, recipes: List[Dict[str, Any]], options: Dict[str, Any]
    ) -> bytes:
        """XML形式でエクスポート（RecipeML互換）"""
        root = ET.Element("recipeml")
        root.set("version", "0.5")
        root.set("exported_at", datetime.now().isoformat())

        for recipe in recipes:
            recipe_elem = ET.SubElement(root, "recipe")

            # 基本情報
            head = ET.SubElement(recipe_elem, "head")
            title = ET.SubElement(head, "title")
            title.text = recipe.get("title", "")

            if recipe.get("description"):
                description = ET.SubElement(head, "description")
                description.text = recipe.get("description", "")

            # メタデータ
            if recipe.get("cooking_time_minutes"):
                time_elem = ET.SubElement(head, "time")
                time_elem.set("unit", "minutes")
                time_elem.text = str(recipe.get("cooking_time_minutes", ""))

            if recipe.get("servings"):
                yield_elem = ET.SubElement(head, "yield")
                yield_elem.text = str(recipe.get("servings", ""))

            if recipe.get("category"):
                category = ET.SubElement(head, "category")
                category.text = recipe.get("category", "")

            # 材料
            ingredients = ET.SubElement(recipe_elem, "ingredients")
            for ing in recipe.get("ingredients", []):
                ing_elem = ET.SubElement(ingredients, "ingredient")
                ing_name = ET.SubElement(ing_elem, "name")
                ing_name.text = ing.get("name", "")

                if ing.get("amount"):
                    ing_amount = ET.SubElement(ing_elem, "amount")
                    ing_amount.text = str(ing.get("amount", ""))

                if ing.get("unit"):
                    ing_unit = ET.SubElement(ing_elem, "unit")
                    ing_unit.text = ing.get("unit", "")

            # 手順
            directions = ET.SubElement(recipe_elem, "directions")
            for idx, step in enumerate(recipe.get("steps", []), 1):
                step_elem = ET.SubElement(directions, "step")
                step_elem.set("number", str(idx))
                step_elem.text = step

        # 整形
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        return xml_str.encode("utf-8")

    def _export_markdown(
        self, recipes: List[Dict[str, Any]], options: Dict[str, Any]
    ) -> bytes:
        """Markdown形式でエクスポート（アイコン多用・色付き対応）"""
        # カラースタイル有効化オプション
        use_colors = options.get("use_colors", True)
        use_icons = options.get("use_icons", True)

        if use_colors:
            md_lines = [
                "# 🍳 レシピ集",
                "",
                f"<div style='color: #666; font-size: 0.9em;'>📅 エクスポート日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</div>",
                "",
                f"<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px 20px; border-radius: 8px; display: inline-block;'>",
                f"📊 レシピ数: <strong>{len(recipes)}件</strong>",
                "</div>",
                "",
                "---",
                "",
            ]
        else:
            md_lines = [
                "# 🍳 レシピ集",
                "",
                f"📅 **エクスポート日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}",
                "",
                f"📊 **レシピ数**: {len(recipes)}件",
                "",
                "---",
                "",
            ]

        for idx, recipe in enumerate(recipes, 1):
            # レシピタイトル（カテゴリーに応じたアイコン）
            title = recipe.get('title', '無題')
            category = recipe.get('category')
            category_icon = self._get_category_icon(category) if use_icons else ''

            if use_colors:
                md_lines.append(f"## <span style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 700;'>{category_icon} {title}</span>")
            else:
                md_lines.append(f"## {category_icon + ' ' if category_icon else ''}{title}")
            md_lines.append("")

            if recipe.get("description"):
                if use_colors:
                    md_lines.append(f"<div style='color: #555; font-style: italic; border-left: 4px solid #667eea; padding-left: 16px; margin: 16px 0;'>")
                    md_lines.append(f"💭 {recipe.get('description', '')}")
                    md_lines.append("</div>")
                else:
                    md_lines.append(f"> 💭 {recipe.get('description', '')}")
                md_lines.append("")

            # メタ情報（カラフルなバッジ風）
            meta_items = []
            if recipe.get("cooking_time_minutes"):
                time_val = recipe.get('cooking_time_minutes')
                if use_colors:
                    meta_items.append(f"<span style='background-color: #FF6B6B; color: white; padding: 4px 12px; border-radius: 16px; font-size: 0.9em;'>⏰ {time_val}分</span>")
                else:
                    meta_items.append(f"⏰ 調理時間: {time_val}分")

            if recipe.get("servings"):
                serving_val = recipe.get('servings')
                if use_colors:
                    meta_items.append(f"<span style='background-color: #4ECDC4; color: white; padding: 4px 12px; border-radius: 16px; font-size: 0.9em;'>👨‍🍳 {serving_val}人分</span>")
                else:
                    meta_items.append(f"👨‍🍳 人数: {serving_val}人分")

            if recipe.get("category"):
                cat_val = recipe.get('category')
                cat_icon = self._get_category_icon(cat_val) if use_icons else '📂'
                if use_colors:
                    meta_items.append(f"<span style='background-color: #95E1D3; color: #2d3436; padding: 4px 12px; border-radius: 16px; font-size: 0.9em;'>{cat_icon} {cat_val}</span>")
                else:
                    meta_items.append(f"{cat_icon} カテゴリー: {cat_val}")

            if meta_items:
                md_lines.append(" ".join(meta_items))
                md_lines.append("")

            # タグ（カラフルなタグ風・タグ別アイコン）
            if recipe.get("tags"):
                md_lines.append("### 🏷️ タグ")
                md_lines.append("")
                if use_colors:
                    tags_html = []
                    tag_colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DFE6E9"]
                    for i, tag in enumerate(recipe.get("tags", [])):
                        color = tag_colors[i % len(tag_colors)]
                        tag_icon = self._get_tag_icon(tag) if use_icons else ''
                        tags_html.append(f"<span style='background-color: {color}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.85em; margin-right: 6px;'>{tag_icon} {tag}</span>")
                    md_lines.append(" ".join(tags_html))
                else:
                    tags_with_icons = []
                    for tag in recipe.get("tags", []):
                        tag_icon = self._get_tag_icon(tag) if use_icons else ''
                        tags_with_icons.append(f"{tag_icon} `{tag}`" if tag_icon else f"`{tag}`")
                    md_lines.append(" ".join(tags_with_icons))
                md_lines.append("")

            # 材料（アイコン付き・色分け）
            if use_colors:
                md_lines.append("### <span style='color: #FF6B6B;'>🥕 材料</span>")
            else:
                md_lines.append("### 🥕 材料")
            md_lines.append("")

            if use_colors:
                md_lines.append("<div style='background-color: #FFF9E6; border: 1px solid #FFE066; border-radius: 8px; padding: 16px;'>")

            for ing in recipe.get("ingredients", []):
                amount = ing.get("amount", "")
                unit = ing.get("unit", "")
                name = ing.get("name", "")
                ing_icon = self._get_ingredient_icon(name) if use_icons else '🔸'
                if use_colors:
                    md_lines.append(f"- {ing_icon} <span style='color: #2d3436; font-weight: 600;'>{name}</span> <span style='color: #636e72;'>{amount} {unit}</span>".strip())
                else:
                    md_lines.append(f"- {ing_icon} {name} {amount} {unit}".strip())

            if use_colors:
                md_lines.append("</div>")
            md_lines.append("")

            # 手順（番号付き・アイコン強調）
            if use_colors:
                md_lines.append("### <span style='color: #4ECDC4;'>📝 手順</span>")
            else:
                md_lines.append("### 📝 手順")
            md_lines.append("")

            if use_colors:
                md_lines.append("<div style='background-color: #E8F5FF; border: 1px solid #74B9FF; border-radius: 8px; padding: 16px;'>")

            for step_idx, step in enumerate(recipe.get("steps", []), 1):
                if use_colors:
                    md_lines.append(f"<div style='margin-bottom: 12px;'>")
                    md_lines.append(f"<span style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 4px 12px; border-radius: 50%; font-weight: bold; margin-right: 8px;'>{step_idx}</span>")
                    md_lines.append(f"<span style='color: #2d3436;'>{step}</span>")
                    md_lines.append("</div>")
                else:
                    md_lines.append(f"{step_idx}. ▶️ {step}")

            if use_colors:
                md_lines.append("</div>")
            md_lines.append("")

            # 区切り線
            if use_colors:
                md_lines.append("<hr style='border: none; height: 2px; background: linear-gradient(to right, #667eea, #764ba2); margin: 32px 0;' />")
            else:
                md_lines.append("---")
            md_lines.append("")

        # フッター
        if use_colors:
            md_lines.extend([
                "",
                "<div style='text-align: center; color: #95a5a6; font-size: 0.85em; margin-top: 32px;'>",
                "✨ Powered by Personal Recipe Intelligence ✨",
                "</div>",
            ])

        markdown_content = "\n".join(md_lines)
        return markdown_content.encode("utf-8")

    def _export_pdf(
        self, recipes: List[Dict[str, Any]], options: Dict[str, Any]
    ) -> bytes:
        """PDF形式でエクスポート（日本語対応）"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        # スタイル設定
        styles = getSampleStyleSheet()

        # 日本語対応スタイル
        try:
            title_style = ParagraphStyle(
                "JapaneseTitle",
                parent=styles["Title"],
                fontName="Japanese",
                fontSize=18,
                leading=24,
            )
            heading_style = ParagraphStyle(
                "JapaneseHeading",
                parent=styles["Heading2"],
                fontName="Japanese",
                fontSize=14,
                leading=18,
            )
            body_style = ParagraphStyle(
                "JapaneseBody",
                parent=styles["BodyText"],
                fontName="Japanese",
                fontSize=10,
                leading=14,
            )
        except Exception:
            # フォントが登録されていない場合はデフォルトスタイル使用
            title_style = styles["Title"]
            heading_style = styles["Heading2"]
            body_style = styles["BodyText"]

        # コンテンツ作成
        story = []

        # タイトルページ
        story.append(Paragraph("レシピ集", title_style))
        story.append(Spacer(1, 0.5 * cm))
        story.append(
            Paragraph(
                f"エクスポート日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}",
                body_style,
            )
        )
        story.append(Paragraph(f"レシピ数: {len(recipes)}件", body_style))
        story.append(PageBreak())

        # 各レシピ
        for idx, recipe in enumerate(recipes):
            # タイトル
            story.append(Paragraph(recipe.get("title", "無題"), title_style))
            story.append(Spacer(1, 0.3 * cm))

            # 説明
            if recipe.get("description"):
                story.append(Paragraph(recipe.get("description", ""), body_style))
                story.append(Spacer(1, 0.3 * cm))

            # メタ情報テーブル
            meta_data = []
            if recipe.get("cooking_time_minutes"):
                meta_data.append(
                    ["調理時間", f"{recipe.get('cooking_time_minutes')}分"]
                )
            if recipe.get("servings"):
                meta_data.append(["人数", f"{recipe.get('servings')}人分"])
            if recipe.get("category"):
                meta_data.append(["カテゴリー", recipe.get("category", "")])
            if recipe.get("tags"):
                meta_data.append(["タグ", ", ".join(recipe.get("tags", []))])

            if meta_data:
                meta_table = Table(meta_data, colWidths=[4 * cm, 12 * cm])
                meta_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("FONTNAME", (0, 0), (-1, -1), "Japanese"),
                            ("FONTSIZE", (0, 0), (-1, -1), 9),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ]
                    )
                )
                story.append(meta_table)
                story.append(Spacer(1, 0.5 * cm))

            # 材料
            story.append(Paragraph("材料", heading_style))
            story.append(Spacer(1, 0.2 * cm))

            ing_data = []
            for ing in recipe.get("ingredients", []):
                amount = ing.get("amount", "")
                unit = ing.get("unit", "")
                name = ing.get("name", "")
                ing_data.append([name, f"{amount} {unit}".strip()])

            if ing_data:
                ing_table = Table(ing_data, colWidths=[10 * cm, 6 * cm])
                ing_table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("FONTNAME", (0, 0), (-1, -1), "Japanese"),
                            ("FONTSIZE", (0, 0), (-1, -1), 9),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ]
                    )
                )
                story.append(ing_table)
                story.append(Spacer(1, 0.5 * cm))

            # 手順
            story.append(Paragraph("手順", heading_style))
            story.append(Spacer(1, 0.2 * cm))

            for step_idx, step in enumerate(recipe.get("steps", []), 1):
                story.append(Paragraph(f"{step_idx}. {step}", body_style))
                story.append(Spacer(1, 0.2 * cm))

            # 次のレシピへ
            if idx < len(recipes) - 1:
                story.append(PageBreak())

        # PDF生成
        doc.build(story)
        return buffer.getvalue()

    def export_recipe_book(
        self, recipes: List[Dict[str, Any]], options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        レシピブック生成（PDF）

        Args:
            recipes: レシピリスト
            options: オプション（theme, title等）

        Returns:
            PDFデータ（バイト列）
        """
        options = options or {}
        options["book_mode"] = True

        return self._export_pdf(recipes, options)

    def export_shopping_list(
        self, recipes: List[Dict[str, Any]], options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        買い物リストエクスポート

        Args:
            recipes: レシピリスト
            options: オプション

        Returns:
            買い物リストデータ
        """
        options = options or {}
        format_type = options.get("format", "markdown")

        # 材料を集約
        ingredient_map: Dict[str, Dict[str, Any]] = {}

        for recipe in recipes:
            for ing in recipe.get("ingredients", []):
                name = ing.get("name", "")
                if not name:
                    continue

                if name not in ingredient_map:
                    ingredient_map[name] = {
                        "name": name,
                        "amount": 0,
                        "unit": ing.get("unit", ""),
                        "recipes": [],
                    }

                # 数量を集計（単純加算、単位は最初のものを使用）
                try:
                    amount = float(ing.get("amount", 0))
                    ingredient_map[name]["amount"] += amount
                except (ValueError, TypeError):
                    pass

                ingredient_map[name]["recipes"].append(recipe.get("title", ""))

        # ソート
        ingredients = sorted(ingredient_map.values(), key=lambda x: x["name"])

        if format_type == "json":
            data = {
                "exported_at": datetime.now().isoformat(),
                "recipe_count": len(recipes),
                "ingredient_count": len(ingredients),
                "ingredients": ingredients,
            }
            return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

        elif format_type == "markdown":
            md_lines = [
                "# 買い物リスト",
                "",
                f"エクスポート日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}",
                "",
                f"対象レシピ数: {len(recipes)}件",
                "",
                "## 材料一覧",
                "",
            ]

            for ing in ingredients:
                amount = ing["amount"] if ing["amount"] > 0 else ""
                unit = ing["unit"]
                name = ing["name"]
                md_lines.append(f"- [ ] {name} {amount} {unit}".strip())

            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")
            md_lines.append("## 使用レシピ")
            md_lines.append("")

            for recipe in recipes:
                md_lines.append(f"- {recipe.get('title', '')}")

            return "\n".join(md_lines).encode("utf-8")

        else:
            raise ValueError(f"Unsupported format for shopping list: {format_type}")

    def export_nutrition_report(
        self, recipes: List[Dict[str, Any]], options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        栄養レポートエクスポート

        Args:
            recipes: レシピリスト
            options: オプション

        Returns:
            栄養レポートデータ
        """
        options = options or {}
        format_type = options.get("format", "json")

        # 栄養情報を集計
        report = {
            "exported_at": datetime.now().isoformat(),
            "recipe_count": len(recipes),
            "recipes": [],
        }

        for recipe in recipes:
            nutrition = recipe.get("nutrition", {})
            recipe_report = {
                "id": recipe.get("id"),
                "title": recipe.get("title", ""),
                "nutrition": {
                    "calories": nutrition.get("calories", 0),
                    "protein": nutrition.get("protein", 0),
                    "fat": nutrition.get("fat", 0),
                    "carbohydrates": nutrition.get("carbohydrates", 0),
                },
            }
            report["recipes"].append(recipe_report)

        if format_type == "json":
            return json.dumps(report, indent=2, ensure_ascii=False).encode("utf-8")

        elif format_type == "csv":
            output = StringIO()
            writer = csv.writer(output)

            headers = [
                "レシピID",
                "タイトル",
                "カロリー (kcal)",
                "タンパク質 (g)",
                "脂質 (g)",
                "炭水化物 (g)",
            ]
            writer.writerow(headers)

            for recipe_report in report["recipes"]:
                nut = recipe_report["nutrition"]
                row = [
                    recipe_report["id"],
                    recipe_report["title"],
                    nut["calories"],
                    nut["protein"],
                    nut["fat"],
                    nut["carbohydrates"],
                ]
                writer.writerow(row)

            csv_content = output.getvalue()
            return b"\xef\xbb\xbf" + csv_content.encode("utf-8")

        else:
            raise ValueError(f"Unsupported format for nutrition report: {format_type}")

    def create_backup(
        self, recipes: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        フルバックアップ作成

        Args:
            recipes: レシピリスト
            metadata: メタデータ

        Returns:
            バックアップファイルパス
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backups_dir / f"backup_{timestamp}.json"

        backup_data = {
            "backup_version": "1.0",
            "created_at": datetime.now().isoformat(),
            "recipe_count": len(recipes),
            "metadata": metadata or {},
            "recipes": recipes,
        }

        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)

        return str(backup_file)

    def restore_backup(self, backup_file: str) -> Dict[str, Any]:
        """
        バックアップからリストア

        Args:
            backup_file: バックアップファイルパス

        Returns:
            リストアしたデータ

        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: 不正なバックアップファイル
        """
        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")

        with open(backup_path, "r", encoding="utf-8") as f:
            backup_data = json.load(f)

        # バージョンチェック
        if backup_data.get("backup_version") != "1.0":
            raise ValueError("Unsupported backup version")

        return backup_data

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        バックアップ一覧を取得

        Returns:
            バックアップ情報のリスト
        """
        backups = []
        for backup_file in sorted(self.backups_dir.glob("backup_*.json"), reverse=True):
            try:
                with open(backup_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                backups.append(
                    {
                        "file": str(backup_file),
                        "filename": backup_file.name,
                        "created_at": data.get("created_at"),
                        "recipe_count": data.get("recipe_count", 0),
                        "size_bytes": backup_file.stat().st_size,
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to read backup file {backup_file}: {e}")
                continue

        return backups
