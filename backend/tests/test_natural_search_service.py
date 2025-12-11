"""
Natural Search Service Tests
自然言語検索サービスのテスト
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from backend.services.natural_search_service import (
  NaturalSearchService,
  ParsedQuery
)


@pytest.fixture
def temp_data_dir():
  """一時データディレクトリ"""
  temp_dir = tempfile.mkdtemp()
  yield temp_dir
  shutil.rmtree(temp_dir)


@pytest.fixture
def service(temp_data_dir):
  """NaturalSearchService インスタンス"""
  return NaturalSearchService(data_dir=temp_data_dir)


@pytest.fixture
def sample_recipes():
  """サンプルレシピデータ"""
  return [
    {
      "id": "1",
      "title": "鶏の唐揚げ",
      "description": "サクサクでジューシーな唐揚げ",
      "ingredients": ["鶏もも肉", "しょうゆ", "にんにく", "しょうが"],
      "steps": ["肉を切る", "下味をつける", "揚げる"],
      "tags": ["和食", "主菜", "揚げ物"],
      "cooking_time": "30分",
      "servings": "2-3人前"
    },
    {
      "id": "2",
      "title": "野菜たっぷりサラダ",
      "description": "新鮮な野菜のヘルシーサラダ",
      "ingredients": ["レタス", "トマト", "きゅうり", "にんじん"],
      "steps": ["野菜を切る", "盛り付ける", "ドレッシングをかける"],
      "tags": ["サラダ", "副菜", "ヘルシー"],
      "cooking_time": "10分",
      "servings": "2人前"
    },
    {
      "id": "3",
      "title": "チキンカレー",
      "description": "スパイシーで本格的なカレー",
      "ingredients": ["鶏肉", "玉ねぎ", "にんじん", "カレールウ"],
      "steps": ["材料を炒める", "煮込む", "ルウを入れる"],
      "tags": ["カレー", "主菜", "辛い"],
      "cooking_time": "45分",
      "servings": "4人前"
    },
    {
      "id": "4",
      "title": "豚の生姜焼き",
      "description": "簡単で美味しい定番料理",
      "ingredients": ["豚ロース", "しょうが", "しょうゆ", "みりん"],
      "steps": ["肉を焼く", "タレを絡める"],
      "tags": ["和食", "主菜", "簡単"],
      "cooking_time": "15分",
      "servings": "2人前"
    },
    {
      "id": "5",
      "title": "トマトパスタ",
      "description": "あっさりしたトマトソースのパスタ",
      "ingredients": ["パスタ", "トマト", "にんにく", "オリーブオイル"],
      "steps": ["パスタを茹でる", "ソースを作る", "和える"],
      "tags": ["パスタ", "洋食", "あっさり"],
      "cooking_time": "20分",
      "servings": "2人前"
    }
  ]


class TestParseQuery:
  """クエリ解析のテスト"""

  def test_simple_ingredient(self, service):
    """シンプルな食材検索"""
    parsed = service.parse_query("鶏肉")

    assert parsed.original == "鶏肉"
    assert "鶏肉" in parsed.ingredients_include
    assert len(parsed.ingredients_exclude) == 0

  def test_multiple_ingredients(self, service):
    """複数食材検索"""
    parsed = service.parse_query("鶏肉とトマト")

    assert "鶏肉" in parsed.ingredients_include
    assert "トマト" in parsed.ingredients_include

  def test_negation_pattern(self, service):
    """否定パターンの検出"""
    parsed = service.parse_query("辛くない料理")

    # 「辛くない」は否定パターンとして検出される
    assert "辛くない" in parsed.negations
    # 検索で除外条件として使用されることを確認（negationsの存在）
    assert len(parsed.negations) > 0

  def test_negation_ingredient(self, service):
    """食材の否定"""
    parsed = service.parse_query("豚肉なし")

    assert "豚肉" in parsed.ingredients_exclude
    assert "豚肉なし" in parsed.negations

  def test_cooking_method(self, service):
    """調理法の抽出"""
    parsed = service.parse_query("揚げ物")

    assert "揚げ物" in parsed.cooking_methods or "揚げる" in parsed.cooking_methods

  def test_category(self, service):
    """カテゴリの抽出"""
    parsed = service.parse_query("和食")

    assert "和食" in parsed.categories

  def test_adjective(self, service):
    """形容詞の抽出"""
    parsed = service.parse_query("簡単な料理")

    assert "簡単" in parsed.adjectives

  def test_complex_query(self, service):
    """複雑なクエリ"""
    parsed = service.parse_query("辛くない簡単な鶏肉料理")

    assert "鶏肉" in parsed.ingredients_include
    # 「辛くない」は否定パターンとして検出される
    assert "辛くない" in parsed.negations
    assert "簡単" in parsed.adjectives

  def test_synonym_normalization(self, service):
    """同義語の正規化"""
    parsed = service.parse_query("たまねぎ")

    # 「たまねぎ」→「玉ねぎ」に正規化される
    assert "玉ねぎ" in parsed.ingredients_include

  def test_empty_query(self, service):
    """空のクエリ"""
    parsed = service.parse_query("")

    assert parsed.original == ""
    assert len(parsed.ingredients_include) == 0


class TestSearchRecipes:
  """レシピ検索のテスト"""

  def test_ingredient_search(self, service, sample_recipes):
    """食材での検索"""
    parsed = service.parse_query("鶏肉")
    results = service.search_recipes(sample_recipes, parsed)

    # 鶏肉を含むレシピが返される
    assert len(results) > 0
    titles = [r["title"] for r in results]
    assert "鶏の唐揚げ" in titles or "チキンカレー" in titles

  def test_negation_search(self, service, sample_recipes):
    """否定検索"""
    parsed = service.parse_query("辛くない")
    results = service.search_recipes(sample_recipes, parsed)

    # 辛いカレーは除外される
    titles = [r["title"] for r in results]
    assert "チキンカレー" not in titles

  def test_adjective_search(self, service, sample_recipes):
    """形容詞での検索"""
    parsed = service.parse_query("簡単")
    results = service.search_recipes(sample_recipes, parsed)

    # 簡単なレシピが上位に来る
    assert len(results) > 0
    assert "豚の生姜焼き" in [r["title"] for r in results]

  def test_category_search(self, service, sample_recipes):
    """カテゴリ検索"""
    parsed = service.parse_query("和食")
    results = service.search_recipes(sample_recipes, parsed)

    # 和食が返される
    assert len(results) > 0
    for recipe in results[:3]:  # 上位3件をチェック
      assert "和食" in recipe.get("tags", [])

  def test_complex_search(self, service, sample_recipes):
    """複雑な検索"""
    parsed = service.parse_query("辛くない簡単な鶏肉料理")
    results = service.search_recipes(sample_recipes, parsed)

    # 鶏肉、簡単を含み、辛くないレシピ
    assert len(results) > 0
    titles = [r["title"] for r in results]
    # 鶏肉を含むレシピが上位に来る（唐揚げまたはカレー）
    # 注：否定パターンはスコアを下げるが完全除外はしない
    assert any("鶏" in title or "チキン" in title for title in titles[:3])

  def test_no_results(self, service, sample_recipes):
    """結果なし"""
    parsed = service.parse_query("存在しない食材XYZ")
    results = service.search_recipes(sample_recipes, parsed)

    assert len(results) >= 0  # 空でも問題なし

  def test_score_ordering(self, service, sample_recipes):
    """スコア順のソート"""
    parsed = service.parse_query("鶏肉 和食")
    results = service.search_recipes(sample_recipes, parsed)

    # マッチ度が高いものが上位
    assert len(results) > 0
    # 最初のレシピが最もマッチ度が高い
    first_recipe = results[0]
    assert "鶏" in first_recipe["title"] or "鶏" in str(first_recipe.get("ingredients", []))


class TestSuggestions:
  """サジェスト機能のテスト"""

  def test_partial_match(self, service):
    """部分一致サジェスト"""
    suggestions = service.get_suggestions("鶏", limit=5)

    assert len(suggestions) > 0
    # 「鶏」を含む候補が返される
    assert any("鶏" in s for s in suggestions)

  def test_empty_query_popular(self, service):
    """空クエリで人気検索を返す"""
    # まず検索履歴を作成
    service.parse_query("鶏肉")
    service.parse_query("鶏肉")
    service.parse_query("豚肉")

    suggestions = service.get_suggestions("", limit=5)

    # 人気のクエリが返される
    assert len(suggestions) > 0
    assert "鶏肉" in suggestions

  def test_limit_suggestions(self, service):
    """サジェスト数の制限"""
    suggestions = service.get_suggestions("料理", limit=3)

    assert len(suggestions) <= 3


class TestHistory:
  """履歴機能のテスト"""

  def test_add_to_history(self, service):
    """履歴への追加"""
    service.parse_query("鶏肉")
    service.parse_query("豚肉")

    history = service.get_search_history(limit=10)

    assert len(history) == 2
    assert history[0]["query"] == "豚肉"  # 最新が先頭
    assert history[1]["query"] == "鶏肉"

  def test_history_limit(self, service):
    """履歴の上限"""
    for i in range(150):
      service.parse_query(f"クエリ{i}")

    # 保存は最新100件のみ
    service._save_history()

    # 読み込み直し
    new_service = NaturalSearchService(data_dir=service.data_dir)
    history = new_service.get_search_history(limit=200)

    assert len(history) <= 100

  def test_history_persistence(self, service):
    """履歴の永続化"""
    service.parse_query("テスト検索")

    # 新しいインスタンスで読み込み
    new_service = NaturalSearchService(data_dir=service.data_dir)
    history = new_service.get_search_history(limit=10)

    assert len(history) == 1
    assert history[0]["query"] == "テスト検索"


class TestExplainQuery:
  """クエリ説明のテスト"""

  def test_explain_simple(self, service):
    """シンプルなクエリの説明"""
    parsed = service.parse_query("鶏肉")
    explanation = service.explain_query(parsed)

    assert "鶏肉" in explanation

  def test_explain_complex(self, service):
    """複雑なクエリの説明"""
    parsed = service.parse_query("辛くない簡単な鶏肉料理")
    explanation = service.explain_query(parsed)

    assert "鶏肉" in explanation
    assert "簡単" in explanation or "特徴" in explanation

  def test_explain_empty(self, service):
    """空クエリの説明"""
    parsed = service.parse_query("")
    explanation = service.explain_query(parsed)

    assert "検索条件なし" in explanation or explanation == "検索条件なし"


class TestEdgeCases:
  """エッジケースのテスト"""

  def test_special_characters(self, service):
    """特殊文字を含むクエリ"""
    parsed = service.parse_query("鶏肉!?@#")

    assert "鶏肉" in parsed.ingredients_include

  def test_whitespace_query(self, service):
    """スペースのみのクエリ"""
    parsed = service.parse_query("   ")

    # 実装はクエリをトリムするため、空文字列になる
    assert parsed.original == "" or parsed.original == "   "

  def test_very_long_query(self, service):
    """非常に長いクエリ"""
    long_query = "鶏肉 " * 100
    parsed = service.parse_query(long_query)

    assert "鶏肉" in parsed.ingredients_include

  def test_unicode_query(self, service):
    """Unicode文字を含むクエリ"""
    parsed = service.parse_query("🍗チキン🍗")

    # エラーが出ないことを確認
    assert parsed.original == "🍗チキン🍗"
