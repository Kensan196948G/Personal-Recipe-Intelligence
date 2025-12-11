"""
エクスポート強化サービスのテスト
"""

import json
import tempfile
from pathlib import Path

import pytest

# reportlabがインストールされていない場合はPDF関連テストをスキップ
try:
  from backend.services.export_enhanced_service import ExportEnhancedService

  EXPORT_SERVICE_AVAILABLE = True
except ImportError:
  EXPORT_SERVICE_AVAILABLE = False


pytestmark = pytest.mark.skipif(
  not EXPORT_SERVICE_AVAILABLE,
  reason="export_enhanced_service requires reportlab",
)


@pytest.fixture
def export_service():
  """エクスポートサービスのフィクスチャ"""
  with tempfile.TemporaryDirectory() as tmpdir:
    service = ExportEnhancedService(data_dir=tmpdir)
    yield service


@pytest.fixture
def sample_recipes():
  """サンプルレシピデータ"""
  return [
    {
      "id": "recipe-001",
      "title": "カレーライス",
      "description": "スパイシーな本格カレー",
      "cooking_time_minutes": 45,
      "servings": 4,
      "category": "main",
      "tags": ["カレー", "スパイス"],
      "ingredients": [
        {"name": "玉ねぎ", "amount": "2", "unit": "個"},
        {"name": "じゃがいも", "amount": "3", "unit": "個"},
        {"name": "にんじん", "amount": "1", "unit": "本"},
        {"name": "豚肉", "amount": "300", "unit": "g"},
      ],
      "steps": [
        "野菜を一口大に切る",
        "肉を炒める",
        "野菜を加えて炒める",
        "水を加えて煮込む",
        "カレールーを入れて完成",
      ],
      "created_at": "2025-01-01T10:00:00",
      "nutrition": {
        "calories": 550,
        "protein": 25,
        "fat": 18,
        "carbohydrates": 65,
      },
    },
    {
      "id": "recipe-002",
      "title": "パスタカルボナーラ",
      "description": "クリーミーなカルボナーラ",
      "cooking_time_minutes": 20,
      "servings": 2,
      "category": "main",
      "tags": ["パスタ", "イタリアン"],
      "ingredients": [
        {"name": "パスタ", "amount": "200", "unit": "g"},
        {"name": "ベーコン", "amount": "100", "unit": "g"},
        {"name": "卵", "amount": "2", "unit": "個"},
        {"name": "粉チーズ", "amount": "50", "unit": "g"},
      ],
      "steps": [
        "パスタを茹でる",
        "ベーコンを炒める",
        "卵と粉チーズを混ぜる",
        "パスタとベーコンを合わせる",
        "卵液を絡めて完成",
      ],
      "created_at": "2025-01-02T12:00:00",
      "nutrition": {
        "calories": 680,
        "protein": 30,
        "fat": 28,
        "carbohydrates": 75,
      },
    },
  ]


def test_get_supported_formats(export_service):
  """対応フォーマット一覧の取得"""
  formats = export_service.get_supported_formats()

  assert "json" in formats
  assert "csv" in formats
  assert "xml" in formats
  assert "markdown" in formats
  assert "pdf" in formats

  assert formats["json"]["mime"] == "application/json"
  assert formats["csv"]["ext"] == ".csv"


def test_export_json(export_service, sample_recipes):
  """JSON形式エクスポート"""
  data = export_service.export_recipes(sample_recipes, format_type="json")

  assert isinstance(data, bytes)
  json_data = json.loads(data.decode("utf-8"))

  assert "exported_at" in json_data
  assert "format_version" in json_data
  assert json_data["recipe_count"] == 2
  assert len(json_data["recipes"]) == 2
  assert json_data["recipes"][0]["title"] == "カレーライス"


def test_export_json_with_options(export_service, sample_recipes):
  """JSON形式エクスポート（オプション付き）"""
  options = {"indent": 4, "ensure_ascii": True}
  data = export_service.export_recipes(
    sample_recipes, format_type="json", options=options
  )

  json_str = data.decode("utf-8")
  assert "    " in json_str  # 4スペースインデント


def test_export_csv(export_service, sample_recipes):
  """CSV形式エクスポート"""
  data = export_service.export_recipes(sample_recipes, format_type="csv")

  assert isinstance(data, bytes)
  csv_str = data.decode("utf-8")

  # BOMチェック
  assert csv_str.startswith("\ufeff")

  # ヘッダーチェック
  assert "ID" in csv_str
  assert "タイトル" in csv_str
  assert "材料" in csv_str

  # データチェック
  assert "カレーライス" in csv_str
  assert "recipe-001" in csv_str


def test_export_xml(export_service, sample_recipes):
  """XML形式エクスポート"""
  data = export_service.export_recipes(sample_recipes, format_type="xml")

  assert isinstance(data, bytes)
  xml_str = data.decode("utf-8")

  # XML構造チェック
  assert '<?xml version="1.0" ?>' in xml_str
  assert "<recipeml" in xml_str
  assert "<recipe>" in xml_str
  assert "<title>カレーライス</title>" in xml_str
  assert "<ingredient>" in xml_str
  assert "<step" in xml_str


def test_export_markdown(export_service, sample_recipes):
  """Markdown形式エクスポート"""
  data = export_service.export_recipes(sample_recipes, format_type="markdown")

  assert isinstance(data, bytes)
  md_str = data.decode("utf-8")

  # Markdown構造チェック
  assert "# レシピ集" in md_str
  assert "## カレーライス" in md_str
  assert "### 材料" in md_str
  assert "### 手順" in md_str
  assert "- 玉ねぎ 2 個" in md_str
  assert "1. 野菜を一口大に切る" in md_str


def test_export_pdf(export_service, sample_recipes):
  """PDF形式エクスポート"""
  data = export_service.export_recipes(sample_recipes, format_type="pdf")

  assert isinstance(data, bytes)
  assert data[:4] == b"%PDF"  # PDFファイルのマジックナンバー
  assert len(data) > 1000  # PDFファイルのサイズチェック


def test_export_unsupported_format(export_service, sample_recipes):
  """未対応フォーマット"""
  with pytest.raises(ValueError, match="Unsupported format"):
    export_service.export_recipes(sample_recipes, format_type="unknown")


def test_export_recipe_book(export_service, sample_recipes):
  """レシピブック生成"""
  options = {"title": "私のレシピブック", "theme": "elegant"}
  data = export_service.export_recipe_book(sample_recipes, options=options)

  assert isinstance(data, bytes)
  assert data[:4] == b"%PDF"
  assert len(data) > 1000


def test_export_shopping_list_markdown(export_service, sample_recipes):
  """買い物リストエクスポート（Markdown）"""
  options = {"format": "markdown"}
  data = export_service.export_shopping_list(sample_recipes, options=options)

  md_str = data.decode("utf-8")

  assert "# 買い物リスト" in md_str
  assert "## 材料一覧" in md_str
  assert "- [ ] 玉ねぎ" in md_str
  assert "- [ ] じゃがいも" in md_str
  assert "- [ ] パスタ" in md_str


def test_export_shopping_list_json(export_service, sample_recipes):
  """買い物リストエクスポート（JSON）"""
  options = {"format": "json"}
  data = export_service.export_shopping_list(sample_recipes, options=options)

  json_data = json.loads(data.decode("utf-8"))

  assert "ingredients" in json_data
  assert json_data["recipe_count"] == 2
  assert json_data["ingredient_count"] > 0

  # 材料の集計確認
  ingredients = json_data["ingredients"]
  ingredient_names = [ing["name"] for ing in ingredients]
  assert "玉ねぎ" in ingredient_names
  assert "パスタ" in ingredient_names


def test_export_nutrition_report_json(export_service, sample_recipes):
  """栄養レポートエクスポート（JSON）"""
  options = {"format": "json"}
  data = export_service.export_nutrition_report(sample_recipes, options=options)

  json_data = json.loads(data.decode("utf-8"))

  assert "recipes" in json_data
  assert json_data["recipe_count"] == 2

  recipe_report = json_data["recipes"][0]
  assert "nutrition" in recipe_report
  assert recipe_report["nutrition"]["calories"] == 550


def test_export_nutrition_report_csv(export_service, sample_recipes):
  """栄養レポートエクスポート（CSV）"""
  options = {"format": "csv"}
  data = export_service.export_nutrition_report(sample_recipes, options=options)

  csv_str = data.decode("utf-8")

  # BOMチェック
  assert csv_str.startswith("\ufeff")

  # ヘッダーチェック
  assert "カロリー" in csv_str
  assert "タンパク質" in csv_str

  # データチェック
  assert "550" in csv_str  # カレーのカロリー
  assert "680" in csv_str  # パスタのカロリー


def test_create_backup(export_service, sample_recipes):
  """バックアップ作成"""
  metadata = {"note": "テストバックアップ"}
  backup_file = export_service.create_backup(sample_recipes, metadata=metadata)

  assert Path(backup_file).exists()
  assert backup_file.endswith(".json")

  # バックアップファイルの内容確認
  with open(backup_file, "r", encoding="utf-8") as f:
    backup_data = json.load(f)

  assert backup_data["backup_version"] == "1.0"
  assert backup_data["recipe_count"] == 2
  assert backup_data["metadata"]["note"] == "テストバックアップ"
  assert len(backup_data["recipes"]) == 2


def test_restore_backup(export_service, sample_recipes):
  """バックアップからリストア"""
  # バックアップ作成
  backup_file = export_service.create_backup(sample_recipes)

  # リストア
  restored_data = export_service.restore_backup(backup_file)

  assert restored_data["backup_version"] == "1.0"
  assert restored_data["recipe_count"] == 2
  assert len(restored_data["recipes"]) == 2
  assert restored_data["recipes"][0]["title"] == "カレーライス"


def test_restore_backup_file_not_found(export_service):
  """存在しないバックアップファイルのリストア"""
  with pytest.raises(FileNotFoundError):
    export_service.restore_backup("nonexistent.json")


def test_restore_backup_invalid_version(export_service):
  """不正なバージョンのバックアップファイル"""
  # 不正なバックアップファイルを作成
  invalid_backup = export_service.backups_dir / "invalid.json"
  with open(invalid_backup, "w", encoding="utf-8") as f:
    json.dump({"backup_version": "2.0"}, f)

  with pytest.raises(ValueError, match="Unsupported backup version"):
    export_service.restore_backup(str(invalid_backup))


def test_list_backups(export_service, sample_recipes):
  """バックアップ一覧取得"""
  # バックアップを複数作成
  export_service.create_backup(sample_recipes, metadata={"note": "Backup 1"})
  export_service.create_backup(sample_recipes, metadata={"note": "Backup 2"})

  backups = export_service.list_backups()

  assert len(backups) == 2
  assert all("file" in b for b in backups)
  assert all("filename" in b for b in backups)
  assert all("created_at" in b for b in backups)
  assert all("recipe_count" in b for b in backups)
  assert all(b["recipe_count"] == 2 for b in backups)


def test_list_backups_empty(export_service):
  """バックアップが存在しない場合"""
  backups = export_service.list_backups()
  assert backups == []


def test_export_empty_recipes(export_service):
  """レシピが空の場合のエクスポート"""
  data = export_service.export_recipes([], format_type="json")

  json_data = json.loads(data.decode("utf-8"))
  assert json_data["recipe_count"] == 0
  assert json_data["recipes"] == []


def test_export_shopping_list_with_duplicate_ingredients(export_service):
  """重複する材料の買い物リスト"""
  recipes = [
    {
      "id": "r1",
      "title": "Recipe 1",
      "ingredients": [
        {"name": "玉ねぎ", "amount": "1", "unit": "個"},
        {"name": "にんじん", "amount": "2", "unit": "本"},
      ],
    },
    {
      "id": "r2",
      "title": "Recipe 2",
      "ingredients": [
        {"name": "玉ねぎ", "amount": "2", "unit": "個"},
        {"name": "じゃがいも", "amount": "3", "unit": "個"},
      ],
    },
  ]

  options = {"format": "json"}
  data = export_service.export_shopping_list(recipes, options=options)

  json_data = json.loads(data.decode("utf-8"))
  ingredients = json_data["ingredients"]

  # 玉ねぎが集計されている
  onion = next((ing for ing in ingredients if ing["name"] == "玉ねぎ"), None)
  assert onion is not None
  assert onion["amount"] == 3.0  # 1 + 2


def test_export_with_missing_fields(export_service):
  """必須フィールドが欠けているレシピ"""
  recipes = [
    {
      "id": "r1",
      "title": "Minimal Recipe",
      # その他のフィールドなし
    }
  ]

  # エクスポートがエラーを起こさないことを確認
  data = export_service.export_recipes(recipes, format_type="json")
  assert isinstance(data, bytes)

  data = export_service.export_recipes(recipes, format_type="csv")
  assert isinstance(data, bytes)

  data = export_service.export_recipes(recipes, format_type="markdown")
  assert isinstance(data, bytes)


def test_concurrent_exports(export_service, sample_recipes):
  """複数のエクスポートを同時実行"""
  # 同時に複数のフォーマットでエクスポート
  json_data = export_service.export_recipes(sample_recipes, format_type="json")
  csv_data = export_service.export_recipes(sample_recipes, format_type="csv")
  md_data = export_service.export_recipes(sample_recipes, format_type="markdown")

  assert isinstance(json_data, bytes)
  assert isinstance(csv_data, bytes)
  assert isinstance(md_data, bytes)

  # それぞれが正しいフォーマットであることを確認
  assert json.loads(json_data.decode("utf-8"))
  assert csv_data.startswith(b"\xef\xbb\xbf")  # BOM
  assert b"# " in md_data  # Markdownヘッダー
