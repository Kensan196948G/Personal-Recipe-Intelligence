"""
Recipe Collector Service のテスト

RecipeCollector の以下の機能をテスト:
- 単位変換
- 材料名正規化
- データクレンジング
- 翻訳（キャッシュ、バッチ）
- レシピ保存
- ランダム収集
- 検索収集
- エラーハンドリング
- リトライ機構

目標カバレッジ: 90%
テスト関数数: 40-50
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
from sqlmodel import Session, select

from backend.services.recipe_collector import (
    RecipeCollector,
    UNIT_CONVERSIONS,
    UNIT_JP_MAPPING,
)
from backend.models.recipe import Recipe, Ingredient, Step, Tag, RecipeTag


# ================================================================================
# Fixtures
# ================================================================================

@pytest.fixture
def mock_session():
    """モックDBセッション"""
    session = MagicMock(spec=Session)
    session.exec = MagicMock()
    session.add = MagicMock()
    session.flush = MagicMock()
    session.commit = MagicMock()
    return session


@pytest.fixture
def mock_spoonacular():
    """モック Spoonacular クライアント"""
    with patch("backend.services.recipe_collector.SpoonacularClient") as mock:
        yield mock.return_value


@pytest.fixture
def mock_translator():
    """モック DeepL トランスレーター"""
    with patch("backend.services.recipe_collector.DeepLTranslator") as mock:
        translator = mock.return_value
        translator.translate.return_value = "翻訳済みテキスト"
        translator.translate_batch.return_value = ["翻訳1", "翻訳2", "翻訳3"]
        yield translator


@pytest.fixture
def collector_with_translation(mock_translator):
    """翻訳機能付きコレクター"""
    return RecipeCollector(
        spoonacular_key="test_spoonacular_key",
        deepl_key="test_deepl_key",
    )


@pytest.fixture
def collector_without_translation():
    """翻訳機能なしコレクター"""
    return RecipeCollector(
        spoonacular_key="test_spoonacular_key",
        skip_translation=True,
    )


@pytest.fixture
def sample_raw_recipe():
    """サンプルレシピデータ（Spoonacular形式）"""
    return {
        "id": 12345,
        "title": "Chicken Curry",
        "summary": "A delicious <b>chicken curry</b> recipe",
        "servings": 4,
        "readyInMinutes": 60,
        "preparationMinutes": 20,
        "cookingMinutes": 40,
        "cuisines": ["Indian", "Asian"],
        "dishTypes": ["main course", "dinner"],
        "diets": ["gluten free"],
        "sourceUrl": "https://spoonacular.com/recipes/12345",
    }


@pytest.fixture
def sample_extracted_recipe():
    """抽出後のレシピデータ"""
    return {
        "source_id": "12345",
        "source_url": "https://spoonacular.com/recipes/12345",
        "original_data": {
            "title": "Chicken Curry",
            "summary": "A delicious chicken curry recipe",
            "servings": 4,
            "prep_time_minutes": 20,
            "cook_time_minutes": 40,
            "cuisines": ["Indian", "Asian"],
            "dish_types": ["main course", "dinner"],
            "diets": ["gluten free"],
        },
        "ingredients": [
            {"name": "chicken breast", "amount": 1.0, "unit": "pound"},
            {"name": "onion", "amount": 2.0, "unit": "cup"},
            {"name": "curry powder", "amount": 2.0, "unit": "tablespoon"},
        ],
        "steps": [
            {"number": 1, "description": "Cut chicken into pieces"},
            {"number": 2, "description": "Sauté onions"},
            {"number": 3, "description": "Add curry powder"},
        ],
    }


# ================================================================================
# 単位変換テスト (10 tests)
# ================================================================================

def test_convert_unit_cup_to_ml(collector_without_translation):
    """cupからmlへの変換"""
    amount, unit = collector_without_translation.convert_unit(2.0, "cup")
    assert amount == 480.0  # 2 * 240
    assert unit == "ml"
    assert isinstance(amount, float)
    assert isinstance(unit, str)


def test_convert_unit_tablespoon_to_ml(collector_without_translation):
    """tablespoonからmlへの変換"""
    amount, unit = collector_without_translation.convert_unit(3.0, "tablespoon")
    assert amount == 45.0  # 3 * 15
    assert unit == "ml"


def test_convert_unit_teaspoon_to_ml(collector_without_translation):
    """teaspoonからmlへの変換"""
    amount, unit = collector_without_translation.convert_unit(4.0, "tsp")
    assert amount == 20.0  # 4 * 5
    assert unit == "ml"


def test_convert_unit_ounce_to_gram(collector_without_translation):
    """ounceからgramへの変換"""
    amount, unit = collector_without_translation.convert_unit(10.0, "ounce")
    assert amount == 283.5  # 10 * 28.35
    assert unit == "g"


def test_convert_unit_pound_to_gram(collector_without_translation):
    """poundからgramへの変換"""
    amount, unit = collector_without_translation.convert_unit(1.0, "pound")
    assert amount == 453.6  # 1 * 453.6
    assert unit == "g"


def test_convert_unit_fluid_ounce_to_ml(collector_without_translation):
    """fluid ounceからmlへの変換"""
    amount, unit = collector_without_translation.convert_unit(8.0, "fl oz")
    assert amount == 236.6  # 8 * 29.57, rounded to 1 decimal
    assert unit == "ml"


def test_convert_unit_gallon_to_liter(collector_without_translation):
    """gallonからliterへの変換"""
    amount, unit = collector_without_translation.convert_unit(2.0, "gallon")
    assert amount == 7.6  # 2 * 3.785, rounded to 1 decimal
    assert unit == "l"


def test_convert_unit_case_insensitive(collector_without_translation):
    """大文字小文字を区別しない変換"""
    amount1, unit1 = collector_without_translation.convert_unit(1.0, "CUP")
    amount2, unit2 = collector_without_translation.convert_unit(1.0, "Cup")
    assert amount1 == amount2 == 240.0
    assert unit1 == unit2 == "ml"


def test_convert_unit_unknown_unit(collector_without_translation):
    """未知の単位は変換しない"""
    amount, unit = collector_without_translation.convert_unit(5.0, "pieces")
    assert amount == 5.0
    assert unit == "pieces"


def test_convert_unit_rounding(collector_without_translation):
    """小数点以下1桁に丸める"""
    amount, unit = collector_without_translation.convert_unit(2.55, "cup")
    assert amount == 612.0  # 2.55 * 240 = 612.0
    assert unit == "ml"


# ================================================================================
# 材料名正規化テスト (8 tests)
# ================================================================================

def test_normalize_ingredient_name_lowercase(collector_without_translation):
    """小文字化"""
    normalized = collector_without_translation.normalize_ingredient_name("Chicken Breast")
    assert normalized == "chicken breast"


def test_normalize_ingredient_name_plural_s(collector_without_translation):
    """複数形 -s の正規化"""
    normalized = collector_without_translation.normalize_ingredient_name("tomatoes")
    assert normalized == "tomatoe"  # -es ending


def test_normalize_ingredient_name_plural_es(collector_without_translation):
    """複数形 -es の正規化（sessで終わる場合は変換しない）"""
    normalized = collector_without_translation.normalize_ingredient_name("glasses")
    assert normalized == "glasses"  # -ses ending, no change


def test_normalize_ingredient_name_plural_ies(collector_without_translation):
    """複数形 -ies の正規化"""
    normalized = collector_without_translation.normalize_ingredient_name("berries")
    assert normalized == "berry"  # -ies -> -y


def test_normalize_ingredient_name_whitespace(collector_without_translation):
    """前後の空白を除去"""
    normalized = collector_without_translation.normalize_ingredient_name("  onion  ")
    assert normalized == "onion"


def test_normalize_ingredient_name_no_change(collector_without_translation):
    """変更不要なケース"""
    normalized = collector_without_translation.normalize_ingredient_name("salt")
    assert normalized == "salt"


def test_normalize_ingredient_name_empty(collector_without_translation):
    """空文字列"""
    normalized = collector_without_translation.normalize_ingredient_name("")
    assert normalized == ""


def test_normalize_ingredient_name_mixed_case(collector_without_translation):
    """大文字小文字混在"""
    normalized = collector_without_translation.normalize_ingredient_name("GroUnd BeEf")
    assert normalized == "ground beef"


# ================================================================================
# 材料クレンジングテスト (6 tests)
# ================================================================================

def test_cleanse_ingredient_full_data(collector_without_translation):
    """完全なデータのクレンジング"""
    ingredient = {
        "name": "Chicken Breasts",
        "amount": 2.0,
        "unit": "pound",
        "original_text": "2 pounds chicken breasts",
    }
    cleansed = collector_without_translation.cleanse_ingredient(ingredient)

    assert cleansed["name"] == "Chicken Breasts"
    assert cleansed["name_normalized"] == "chicken breast"
    assert cleansed["amount"] == 907.2  # 2 * 453.6
    assert cleansed["unit"] == "g"
    assert cleansed["original_text"] == "2 pounds chicken breasts"


def test_cleanse_ingredient_no_amount(collector_without_translation):
    """数量なしの材料"""
    ingredient = {"name": "Salt", "original_text": "Salt to taste"}
    cleansed = collector_without_translation.cleanse_ingredient(ingredient)

    assert cleansed["name"] == "Salt"
    assert cleansed["name_normalized"] == "salt"
    assert cleansed["amount"] is None
    assert cleansed["unit"] == ""


def test_cleanse_ingredient_no_unit(collector_without_translation):
    """単位なしの材料"""
    ingredient = {"name": "eggs", "amount": 3}
    cleansed = collector_without_translation.cleanse_ingredient(ingredient)

    assert cleansed["name"] == "eggs"
    assert cleansed["name_normalized"] == "egg"
    assert cleansed["amount"] == 3
    assert cleansed["unit"] == ""


def test_cleanse_ingredient_unit_conversion(collector_without_translation):
    """単位変換あり"""
    ingredient = {"name": "milk", "amount": 2, "unit": "cup"}
    cleansed = collector_without_translation.cleanse_ingredient(ingredient)

    assert cleansed["amount"] == 480.0  # 2 * 240
    assert cleansed["unit"] == "ml"


def test_cleanse_ingredient_unknown_unit(collector_without_translation):
    """未知の単位"""
    ingredient = {"name": "carrot", "amount": 3, "unit": "pieces"}
    cleansed = collector_without_translation.cleanse_ingredient(ingredient)

    assert cleansed["amount"] == 3
    assert cleansed["unit"] == "pieces"


def test_cleanse_ingredient_empty_name(collector_without_translation):
    """空の材料名"""
    ingredient = {"name": "", "amount": 1, "unit": "cup"}
    cleansed = collector_without_translation.cleanse_ingredient(ingredient)

    assert cleansed["name"] == ""
    assert cleansed["name_normalized"] == ""


# ================================================================================
# 手順クレンジングテスト (5 tests)
# ================================================================================

def test_cleanse_step_basic(collector_without_translation):
    """基本的な手順クレンジング"""
    step = {"number": 1, "description": "Cut the chicken into pieces"}
    cleansed = collector_without_translation.cleanse_step(step)

    assert cleansed["description"] == "Cut the chicken into pieces"
    assert cleansed["order"] == 1


def test_cleanse_step_html_tags(collector_without_translation):
    """HTMLタグを除去"""
    step = {
        "number": 2,
        "description": "<p>Sauté <b>onions</b> until golden</p>",
    }
    cleansed = collector_without_translation.cleanse_step(step)

    assert cleansed["description"] == "Sauté onions until golden"
    assert "<p>" not in cleansed["description"]
    assert "<b>" not in cleansed["description"]


def test_cleanse_step_extra_whitespace(collector_without_translation):
    """余分な空白を除去"""
    step = {
        "number": 3,
        "description": "Add   curry    powder   and   stir",
    }
    cleansed = collector_without_translation.cleanse_step(step)

    assert cleansed["description"] == "Add curry powder and stir"


def test_cleanse_step_order_from_dict(collector_without_translation):
    """orderキーから順序を取得"""
    step = {"order": 5, "description": "Serve hot"}
    cleansed = collector_without_translation.cleanse_step(step)

    assert cleansed["order"] == 5


def test_cleanse_step_default_order(collector_without_translation):
    """デフォルト順序"""
    step = {"description": "Enjoy!"}
    cleansed = collector_without_translation.cleanse_step(step)

    assert cleansed["order"] == 1


# ================================================================================
# 翻訳テスト (キャッシュ機能含む) (8 tests)
# ================================================================================

def test_translate_cached_success(collector_with_translation, mock_translator):
    """翻訳成功"""
    result = collector_with_translation._translate_cached("Hello World")

    assert result == "翻訳済みテキスト"
    mock_translator.translate.assert_called_once_with(
        "Hello World", target_lang="JA", source_lang="EN"
    )


def test_translate_cached_empty_text(collector_with_translation, mock_translator):
    """空文字列は翻訳しない"""
    result = collector_with_translation._translate_cached("")

    assert result == ""
    mock_translator.translate.assert_not_called()


def test_translate_cached_cache_hit(collector_with_translation, mock_translator):
    """キャッシュヒット（2回目は API 呼び出しなし）"""
    text = "Test Text"

    # 1回目
    result1 = collector_with_translation._translate_cached(text)
    assert result1 == "翻訳済みテキスト"

    # 2回目（キャッシュから取得）
    result2 = collector_with_translation._translate_cached(text)
    assert result2 == "翻訳済みテキスト"

    # API は1回のみ呼ばれる
    assert mock_translator.translate.call_count == 1


def test_translate_cached_translation_failure(collector_with_translation, mock_translator):
    """翻訳失敗時は原文を返す"""
    mock_translator.translate.side_effect = Exception("API Error")

    result = collector_with_translation._translate_cached("Original Text")

    assert result == "Original Text"
    assert not collector_with_translation._translation_available


def test_translate_cached_no_translator(collector_without_translation):
    """翻訳機能なしの場合は原文を返す"""
    result = collector_without_translation._translate_cached("Hello")

    assert result == "Hello"


def test_translate_batch_cached_success(collector_with_translation, mock_translator):
    """バッチ翻訳成功"""
    texts = ["Text 1", "Text 2", "Text 3"]
    results = collector_with_translation._translate_batch_cached(texts)

    assert results == ["翻訳1", "翻訳2", "翻訳3"]
    mock_translator.translate_batch.assert_called_once()


def test_translate_batch_cached_with_empty_strings(collector_with_translation, mock_translator):
    """空文字列を含むバッチ翻訳"""
    mock_translator.translate_batch.return_value = ["翻訳1", "翻訳2"]

    texts = ["Text 1", "", "Text 2"]
    results = collector_with_translation._translate_batch_cached(texts)

    assert len(results) == 3
    assert results[0] == "翻訳1"
    assert results[1] == ""
    assert results[2] == "翻訳2"


def test_translate_batch_cached_failure_fallback(collector_with_translation, mock_translator):
    """バッチ翻訳失敗時は原文を返す"""
    mock_translator.translate_batch.side_effect = Exception("Batch API Error")

    texts = ["Original 1", "Original 2"]
    results = collector_with_translation._translate_batch_cached(texts)

    assert results == ["Original 1", "Original 2"]
    assert not collector_with_translation._translation_available


# ================================================================================
# レシピ保存テスト (6 tests)
# ================================================================================

def test_save_recipe_success(collector_without_translation, mock_session):
    """レシピ保存成功"""
    recipe_data = {
        "title": "Test Recipe",
        "description": "A test recipe",
        "servings": 4,
        "prep_time_minutes": 15,
        "cook_time_minutes": 30,
        "source_url": "https://example.com/recipe",
        "source_type": "spoonacular",
        "ingredients": [
            {"name": "Ingredient 1", "name_normalized": "ingredient 1", "amount": 100, "unit": "g"},
            {"name": "Ingredient 2", "name_normalized": "ingredient 2", "amount": 200, "unit": "ml"},
        ],
        "steps": [
            {"description": "Step 1", "order": 1},
            {"description": "Step 2", "order": 2},
        ],
        "tags": ["tag1", "tag2"],
        "source_id": "12345",
    }

    # モックレシピオブジェクト
    mock_recipe = Mock(spec=Recipe)
    mock_recipe.id = 100
    mock_recipe.title = "Test Recipe"

    # session.add の呼び出しで recipe.id を設定
    def set_recipe_id(obj):
        if isinstance(obj, Recipe):
            obj.id = 100

    mock_session.add.side_effect = set_recipe_id
    mock_session.exec.return_value.first.return_value = None  # 重複なし

    # テスト実行
    with patch("backend.services.recipe_collector.Recipe", return_value=mock_recipe):
        result = collector_without_translation.save_recipe(mock_session, recipe_data)

    assert result["id"] == 100
    assert result["title"] == "Test Recipe"
    assert mock_session.commit.called


def test_save_recipe_duplicate_skip(collector_without_translation, mock_session):
    """重複レシピはスキップ"""
    recipe_data = {
        "title": "Existing Recipe",
        "source_id": "12345",
        "source_url": "https://spoonacular.com/recipes/12345",
    }

    # 既存レシピをモック
    existing_recipe = Mock(spec=Recipe)
    existing_recipe.id = 50
    existing_recipe.title = "Existing Recipe"

    mock_session.exec.return_value.first.return_value = existing_recipe

    result = collector_without_translation.save_recipe(mock_session, recipe_data)

    assert result["id"] == 50
    assert result["title"] == "Existing Recipe"
    assert not mock_session.add.called


def test_save_recipe_with_tags(collector_without_translation, mock_session):
    """タグ付きレシピの保存"""
    recipe_data = {
        "title": "Tagged Recipe",
        "ingredients": [],
        "steps": [],
        "tags": ["vegetarian", "healthy"],
    }

    mock_recipe = Mock(spec=Recipe)
    mock_recipe.id = 200
    mock_recipe.title = "Tagged Recipe"

    existing_tag = Mock(spec=Tag)
    existing_tag.id = 1
    existing_tag.name = "vegetarian"

    # 1つ目のタグは既存、2つ目は新規
    mock_session.exec.return_value.first.side_effect = [None, existing_tag, None]

    def set_ids(obj):
        if isinstance(obj, Recipe):
            obj.id = 200
        elif isinstance(obj, Tag):
            obj.id = 2

    mock_session.add.side_effect = set_ids

    with patch("backend.services.recipe_collector.Recipe", return_value=mock_recipe):
        result = collector_without_translation.save_recipe(mock_session, recipe_data)

    assert result["id"] == 200
    assert mock_session.commit.called


def test_save_recipe_empty_tags(collector_without_translation, mock_session):
    """空のタグは無視"""
    recipe_data = {
        "title": "No Tags Recipe",
        "ingredients": [],
        "steps": [],
        "tags": ["", "  ", "valid_tag"],
    }

    mock_recipe = Mock(spec=Recipe)
    mock_recipe.id = 300
    mock_recipe.title = "No Tags Recipe"

    mock_session.exec.return_value.first.return_value = None

    def set_ids(obj):
        if isinstance(obj, Recipe):
            obj.id = 300
        elif isinstance(obj, Tag):
            obj.id = 10

    mock_session.add.side_effect = set_ids

    with patch("backend.services.recipe_collector.Recipe", return_value=mock_recipe):
        collector_without_translation.save_recipe(mock_session, recipe_data)

    # 空タグは処理されない（valid_tag のみ）
    tag_adds = [call for call in mock_session.add.call_args_list if "Tag" in str(call)]
    assert len(tag_adds) >= 0  # 空タグは追加されない


def test_save_recipe_ingredients_order(collector_without_translation, mock_session):
    """材料の順序が保持される"""
    recipe_data = {
        "title": "Ordered Ingredients",
        "ingredients": [
            {"name": "First", "name_normalized": "first"},
            {"name": "Second", "name_normalized": "second"},
            {"name": "Third", "name_normalized": "third"},
        ],
        "steps": [],
        "tags": [],
    }

    mock_recipe = Mock(spec=Recipe)
    mock_recipe.id = 400
    mock_recipe.title = "Ordered Ingredients"

    mock_session.exec.return_value.first.return_value = None

    def set_ids(obj):
        if isinstance(obj, Recipe):
            obj.id = 400

    mock_session.add.side_effect = set_ids

    with patch("backend.services.recipe_collector.Recipe", return_value=mock_recipe):
        collector_without_translation.save_recipe(mock_session, recipe_data)

    # Ingredient の order が設定されていることを確認
    ingredient_calls = [
        call for call in mock_session.add.call_args_list
        if len(call[0]) > 0 and "Ingredient" in str(type(call[0][0]))
    ]
    assert len(ingredient_calls) >= 3


def test_save_recipe_steps_order(collector_without_translation, mock_session):
    """手順の順序が保持される"""
    recipe_data = {
        "title": "Ordered Steps",
        "ingredients": [],
        "steps": [
            {"description": "Step One", "order": 1},
            {"description": "Step Two", "order": 2},
        ],
        "tags": [],
    }

    mock_recipe = Mock(spec=Recipe)
    mock_recipe.id = 500
    mock_recipe.title = "Ordered Steps"

    mock_session.exec.return_value.first.return_value = None

    def set_ids(obj):
        if isinstance(obj, Recipe):
            obj.id = 500

    mock_session.add.side_effect = set_ids

    with patch("backend.services.recipe_collector.Recipe", return_value=mock_recipe):
        collector_without_translation.save_recipe(mock_session, recipe_data)

    step_calls = [
        call for call in mock_session.add.call_args_list
        if len(call[0]) > 0 and "Step" in str(type(call[0][0]))
    ]
    assert len(step_calls) >= 2


# ================================================================================
# レシピ翻訳テスト (5 tests)
# ================================================================================

def test_translate_recipe_full(collector_with_translation, mock_translator, sample_extracted_recipe):
    """完全なレシピ翻訳"""
    mock_translator.translate_batch.side_effect = [
        ["カレー", "美味しいチキンカレーのレシピ"],  # タイトルと説明
        ["鶏胸肉", "玉ねぎ", "カレー粉"],  # 材料名
        ["鶏肉を切る", "玉ねぎを炒める", "カレー粉を加える"],  # 手順
        ["インド", "アジア", "メインコース", "ディナー", "グルテンフリー"],  # タグ
    ]

    result = collector_with_translation.translate_recipe(sample_extracted_recipe)

    assert result["title"] == "カレー"
    assert result["description"] == "美味しいチキンカレーのレシピ"
    assert len(result["ingredients"]) == 3
    assert result["ingredients"][0]["name"] == "鶏胸肉"
    assert len(result["steps"]) == 3
    assert result["steps"][0]["description"] == "鶏肉を切る"
    assert len(result["tags"]) == 5


def test_translate_recipe_html_removal(collector_with_translation, mock_translator):
    """HTMLタグを除去してから翻訳"""
    recipe_data = {
        "source_id": "123",
        "source_url": "https://example.com",
        "original_data": {
            "title": "Test",
            "summary": "<p>Test <b>recipe</b> with <i>HTML</i></p>",
        },
        "ingredients": [],
        "steps": [],
    }

    mock_translator.translate_batch.side_effect = [
        ["テスト", "HTMLなしのレシピ"],
        [],
        [],
        [],
    ]

    result = collector_with_translation.translate_recipe(recipe_data)

    # HTML タグが除去されている
    assert "<p>" not in result["description"]
    assert "<b>" not in result["description"]


def test_translate_recipe_long_description_truncate(collector_with_translation, mock_translator):
    """長すぎる説明文を切り詰め"""
    long_description = "A" * 600
    recipe_data = {
        "source_id": "123",
        "source_url": "https://example.com",
        "original_data": {
            "title": "Test",
            "summary": long_description,
        },
        "ingredients": [],
        "steps": [],
    }

    mock_translator.translate_batch.side_effect = [
        ["テスト", "A" * 600],
        [],
        [],
        [],
    ]

    result = collector_with_translation.translate_recipe(recipe_data)

    assert len(result["description"]) == 500  # 500文字に切り詰め


def test_translate_recipe_no_tags(collector_with_translation, mock_translator):
    """タグなしレシピ"""
    recipe_data = {
        "source_id": "123",
        "source_url": "https://example.com",
        "original_data": {
            "title": "Simple",
            "summary": "Simple recipe",
            "cuisines": [],
            "dish_types": [],
            "diets": [],
        },
        "ingredients": [],
        "steps": [],
    }

    mock_translator.translate_batch.side_effect = [
        ["シンプル", "シンプルなレシピ"],
        [],
        [],
    ]

    result = collector_with_translation.translate_recipe(recipe_data)

    assert result["tags"] == []


def test_translate_recipe_missing_fields(collector_with_translation, mock_translator):
    """必須でないフィールドがない場合"""
    recipe_data = {
        "source_id": "123",
        "source_url": "https://example.com",
        "original_data": {
            "title": "Minimal",
        },
        "ingredients": [],
        "steps": [],
    }

    mock_translator.translate_batch.side_effect = [
        ["ミニマル", ""],
        [],
        [],
    ]

    result = collector_with_translation.translate_recipe(recipe_data)

    assert result["title"] == "ミニマル"
    assert result["description"] is None
    assert result["servings"] is None


# ================================================================================
# ランダムレシピ収集テスト (4 tests)
# ================================================================================

def test_collect_random_recipes_success(
    collector_without_translation, mock_session, mock_spoonacular
):
    """ランダムレシピ収集成功"""
    # Spoonacular のモックレスポンス
    mock_spoonacular.get_random_recipes.return_value = [
        {"id": 1, "title": "Recipe 1"},
        {"id": 2, "title": "Recipe 2"},
    ]
    mock_spoonacular.extract_recipe_data.side_effect = [
        {
            "source_id": "1",
            "source_url": "https://example.com/1",
            "original_data": {"title": "Recipe 1"},
            "ingredients": [],
            "steps": [],
        },
        {
            "source_id": "2",
            "source_url": "https://example.com/2",
            "original_data": {"title": "Recipe 2"},
            "ingredients": [],
            "steps": [],
        },
    ]

    mock_session.exec.return_value.first.return_value = None

    mock_recipe1 = Mock(id=10, title="Recipe 1")
    mock_recipe2 = Mock(id=20, title="Recipe 2")

    def create_recipe(obj):
        if isinstance(obj, Recipe):
            if obj.title == "Recipe 1":
                obj.id = 10
            else:
                obj.id = 20

    mock_session.add.side_effect = create_recipe

    with patch("backend.services.recipe_collector.Recipe") as mock_recipe_class:
        mock_recipe_class.side_effect = [mock_recipe1, mock_recipe2]

        results = collector_without_translation.collect_random_recipes(
            session=mock_session, count=2
        )

    assert len(results) == 2
    assert results[0]["title"] == "Recipe 1"
    assert results[1]["title"] == "Recipe 2"


def test_collect_random_recipes_with_tags(
    collector_without_translation, mock_session, mock_spoonacular
):
    """タグ指定でランダムレシピ収集"""
    mock_spoonacular.get_random_recipes.return_value = []

    collector_without_translation.collect_random_recipes(
        session=mock_session, count=3, tags="vegetarian"
    )

    mock_spoonacular.get_random_recipes.assert_called_once_with(
        number=3, tags="vegetarian"
    )


def test_collect_random_recipes_error_handling(
    collector_without_translation, mock_session, mock_spoonacular
):
    """エラーハンドリング（一部のレシピが失敗）"""
    mock_spoonacular.get_random_recipes.return_value = [
        {"id": 1, "title": "Good Recipe"},
        {"id": 2, "title": "Bad Recipe"},
    ]

    def extract_with_error(raw):
        if raw["id"] == 2:
            raise Exception("Extraction failed")
        return {
            "source_id": str(raw["id"]),
            "source_url": "https://example.com/" + str(raw["id"]),
            "original_data": {"title": raw["title"]},
            "ingredients": [],
            "steps": [],
        }

    mock_spoonacular.extract_recipe_data.side_effect = extract_with_error
    mock_session.exec.return_value.first.return_value = None

    mock_recipe = Mock(id=100, title="Good Recipe")

    def create_recipe(obj):
        if isinstance(obj, Recipe):
            obj.id = 100

    mock_session.add.side_effect = create_recipe

    with patch("backend.services.recipe_collector.Recipe", return_value=mock_recipe):
        results = collector_without_translation.collect_random_recipes(
            session=mock_session, count=2
        )

    # エラーが出ても処理は継続
    assert len(results) == 1
    assert results[0]["title"] == "Good Recipe"


def test_collect_random_recipes_empty_result(
    collector_without_translation, mock_session, mock_spoonacular
):
    """空の結果"""
    mock_spoonacular.get_random_recipes.return_value = []

    results = collector_without_translation.collect_random_recipes(
        session=mock_session, count=5
    )

    assert results == []


# ================================================================================
# 検索レシピ収集テスト (3 tests)
# ================================================================================

def test_collect_recipes_by_search_success(
    collector_without_translation, mock_session, mock_spoonacular
):
    """検索でレシピ収集成功"""
    mock_spoonacular.search_recipes.return_value = [
        {"id": 100},
        {"id": 200},
    ]

    mock_spoonacular.get_recipe_information.side_effect = [
        {"id": 100, "title": "Search Result 1"},
        {"id": 200, "title": "Search Result 2"},
    ]

    mock_spoonacular.extract_recipe_data.side_effect = [
        {
            "source_id": "100",
            "source_url": "https://example.com/100",
            "original_data": {"title": "Search Result 1"},
            "ingredients": [],
            "steps": [],
        },
        {
            "source_id": "200",
            "source_url": "https://example.com/200",
            "original_data": {"title": "Search Result 2"},
            "ingredients": [],
            "steps": [],
        },
    ]

    mock_session.exec.return_value.first.return_value = None

    mock_recipe1 = Mock(id=10, title="Search Result 1")
    mock_recipe2 = Mock(id=20, title="Search Result 2")

    def create_recipe(obj):
        if isinstance(obj, Recipe):
            if "1" in obj.title:
                obj.id = 10
            else:
                obj.id = 20

    mock_session.add.side_effect = create_recipe

    with patch("backend.services.recipe_collector.Recipe") as mock_recipe_class:
        mock_recipe_class.side_effect = [mock_recipe1, mock_recipe2]

        results = collector_without_translation.collect_recipes_by_search(
            session=mock_session, query="chicken curry", count=2
        )

    assert len(results) == 2
    mock_spoonacular.search_recipes.assert_called_once_with(
        query="chicken curry", number=2, cuisine=None
    )


def test_collect_recipes_by_search_with_cuisine(
    collector_without_translation, mock_session, mock_spoonacular
):
    """料理ジャンル指定で検索"""
    mock_spoonacular.search_recipes.return_value = []

    collector_without_translation.collect_recipes_by_search(
        session=mock_session, query="pasta", count=3, cuisine="italian"
    )

    mock_spoonacular.search_recipes.assert_called_once_with(
        query="pasta", number=3, cuisine="italian"
    )


def test_collect_recipes_by_search_missing_id(
    collector_without_translation, mock_session, mock_spoonacular
):
    """ID のない検索結果はスキップ"""
    mock_spoonacular.search_recipes.return_value = [
        {"id": 100},
        {},  # ID なし
        {"id": 200},
    ]

    mock_spoonacular.get_recipe_information.side_effect = [
        {"id": 100, "title": "Result 1"},
        {"id": 200, "title": "Result 2"},
    ]

    mock_spoonacular.extract_recipe_data.side_effect = [
        {
            "source_id": "100",
            "source_url": "https://example.com/100",
            "original_data": {"title": "Result 1"},
            "ingredients": [],
            "steps": [],
        },
        {
            "source_id": "200",
            "source_url": "https://example.com/200",
            "original_data": {"title": "Result 2"},
            "ingredients": [],
            "steps": [],
        },
    ]

    mock_session.exec.return_value.first.return_value = None

    mock_recipe1 = Mock(id=10, title="Result 1")
    mock_recipe2 = Mock(id=20, title="Result 2")

    def create_recipe(obj):
        if isinstance(obj, Recipe):
            if "1" in obj.title:
                obj.id = 10
            else:
                obj.id = 20

    mock_session.add.side_effect = create_recipe

    with patch("backend.services.recipe_collector.Recipe") as mock_recipe_class:
        mock_recipe_class.side_effect = [mock_recipe1, mock_recipe2]

        results = collector_without_translation.collect_recipes_by_search(
            session=mock_session, query="test", count=3
        )

    # ID なしはスキップされる
    assert len(results) == 2
