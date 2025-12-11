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
    """Markdown形式でエクスポート"""
    md_lines = [
      "# レシピ集",
      "",
      f"エクスポート日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}",
      "",
      f"レシピ数: {len(recipes)}件",
      "",
      "---",
      "",
    ]

    for recipe in recipes:
      md_lines.append(f"## {recipe.get('title', '無題')}")
      md_lines.append("")

      if recipe.get("description"):
        md_lines.append(recipe.get("description", ""))
        md_lines.append("")

      # メタ情報
      meta_info = []
      if recipe.get("cooking_time_minutes"):
        meta_info.append(f"調理時間: {recipe.get('cooking_time_minutes')}分")
      if recipe.get("servings"):
        meta_info.append(f"人数: {recipe.get('servings')}人分")
      if recipe.get("category"):
        meta_info.append(f"カテゴリー: {recipe.get('category')}")

      if meta_info:
        md_lines.append(" | ".join(meta_info))
        md_lines.append("")

      # タグ
      if recipe.get("tags"):
        tags_str = " ".join([f"`{tag}`" for tag in recipe.get("tags", [])])
        md_lines.append(f"タグ: {tags_str}")
        md_lines.append("")

      # 材料
      md_lines.append("### 材料")
      md_lines.append("")
      for ing in recipe.get("ingredients", []):
        amount = ing.get("amount", "")
        unit = ing.get("unit", "")
        name = ing.get("name", "")
        md_lines.append(f"- {name} {amount} {unit}".strip())
      md_lines.append("")

      # 手順
      md_lines.append("### 手順")
      md_lines.append("")
      for idx, step in enumerate(recipe.get("steps", []), 1):
        md_lines.append(f"{idx}. {step}")
      md_lines.append("")

      md_lines.append("---")
      md_lines.append("")

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
