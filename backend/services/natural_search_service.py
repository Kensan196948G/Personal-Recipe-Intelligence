"""
Natural Language Search Service
自然言語検索サービス - 日本語クエリの解析と検索
"""

import re
import json
from typing import Dict, List, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class ParsedQuery:
  """解析されたクエリ情報"""
  original: str
  ingredients_include: List[str]
  ingredients_exclude: List[str]
  cooking_methods: List[str]
  categories: List[str]
  adjectives: List[str]
  negations: List[str]
  keywords: List[str]


class NaturalSearchService:
  """自然言語検索サービス"""

  def __init__(self, data_dir: str = "data"):
    self.data_dir = Path(data_dir)
    self.data_dir.mkdir(exist_ok=True)

    # 料理ドメイン辞書
    self.dictionary = self._load_dictionary()

    # 検索履歴
    self.history_file = self.data_dir / "search_history.json"
    self.history = self._load_history()

  def _load_dictionary(self) -> Dict[str, List[str]]:
    """料理ドメイン辞書の読み込み"""
    return {
      "ingredients": [
        # 野菜
        "トマト", "きゅうり", "キャベツ", "レタス", "白菜", "ほうれん草",
        "小松菜", "にんじん", "人参", "大根", "玉ねぎ", "たまねぎ", "ねぎ",
        "長ねぎ", "なす", "茄子", "ピーマン", "パプリカ", "じゃがいも",
        "さつまいも", "かぼちゃ", "ブロッコリー", "もやし", "きのこ",
        "しいたけ", "えのき", "しめじ", "まいたけ", "エリンギ",

        # 肉類
        "豚肉", "牛肉", "鶏肉", "鶏もも肉", "鶏むね肉", "ひき肉",
        "豚バラ", "豚ロース", "牛バラ", "ベーコン", "ソーセージ",
        "ハム", "鶏ささみ", "手羽先", "手羽元",

        # 魚介類
        "鮭", "さけ", "サーモン", "まぐろ", "マグロ", "さば", "サバ",
        "あじ", "アジ", "さんま", "サンマ", "いわし", "イワシ", "ぶり",
        "ブリ", "たら", "タラ", "えび", "エビ", "いか", "イカ", "たこ",
        "タコ", "あさり", "アサリ", "しじみ", "シジミ", "ホタテ",

        # 調味料・加工品
        "しょうゆ", "醤油", "みそ", "味噌", "塩", "こしょう", "胡椒",
        "砂糖", "みりん", "酒", "酢", "油", "ごま油", "オリーブオイル",
        "バター", "マヨネーズ", "ケチャップ", "ソース", "めんつゆ",
        "だし", "コンソメ", "チーズ", "牛乳", "豆腐", "納豆", "卵",

        # 穀物・麺類
        "米", "ご飯", "パン", "パスタ", "スパゲッティ", "うどん",
        "そば", "そうめん", "ラーメン", "中華麺", "餃子の皮",

        # その他
        "にんにく", "しょうが", "生姜", "唐辛子", "わさび", "からし",
        "のり", "海苔", "わかめ", "昆布", "梅干し", "漬物",
      ],

      "cooking_methods": [
        "焼く", "炒める", "煮る", "茹でる", "揚げる", "蒸す", "和える",
        "漬ける", "炊く", "グリル", "ソテー", "ロースト", "フライ",
        "天ぷら", "唐揚げ", "から揚げ", "照り焼き", "煮込み", "煮物",
        "炒め物", "サラダ", "刺身", "焼き物", "蒸し物", "揚げ物",
        "レンジ", "電子レンジ", "圧力鍋", "フライパン", "鍋",
      ],

      "categories": [
        "和食", "洋食", "中華", "イタリアン", "フレンチ", "エスニック",
        "韓国料理", "タイ料理", "インド料理", "メキシカン",
        "主菜", "副菜", "汁物", "スープ", "サラダ", "前菜", "おつまみ",
        "ご飯もの", "麺類", "丼", "カレー", "シチュー", "パスタ",
        "デザート", "スイーツ", "お菓子", "パン", "朝食", "昼食",
        "夕食", "弁当", "作り置き", "常備菜",
      ],

      "adjectives": [
        # 味
        "辛い", "甘い", "しょっぱい", "酸っぱい", "苦い", "旨い",
        "美味しい", "おいしい", "濃い", "薄い", "あっさり", "こってり",

        # 難易度・時間
        "簡単", "かんたん", "手軽", "時短", "早い", "速い", "はやい",
        "難しい", "本格", "本格的", "手間", "時間",

        # 健康・栄養
        "ヘルシー", "健康", "ダイエット", "低カロリー", "高たんぱく",
        "高タンパク", "野菜たっぷり", "栄養", "バランス",

        # 食感・温度
        "やわらかい", "柔らかい", "固い", "硬い", "サクサク", "もちもち",
        "ふわふわ", "とろとろ", "熱い", "温かい", "冷たい", "冷製",

        # ボリューム
        "ボリューム", "がっつり", "たっぷり", "少なめ", "軽め",
      ],

      "negation_patterns": [
        "ない", "なし", "抜き", "除く", "以外", "じゃない", "ではない",
        "使わない", "入れない", "入っていない", "不使用", "フリー",
      ],

      "synonyms": {
        "玉ねぎ": ["たまねぎ", "タマネギ", "オニオン"],
        "じゃがいも": ["ジャガイモ", "ポテト"],
        "にんじん": ["人参", "ニンジン", "キャロット"],
        "トマト": ["とまと", "tomato"],
        "鶏肉": ["とり肉", "チキン"],
        "豚肉": ["ぶた肉", "ポーク"],
        "牛肉": ["ぎゅうにく", "ビーフ"],
        "卵": ["たまご", "玉子", "エッグ"],
        "簡単": ["かんたん", "カンタン", "easy"],
        "ヘルシー": ["健康的", "健康", "healthy"],
      }
    }

  def _load_history(self) -> List[Dict]:
    """検索履歴の読み込み"""
    if self.history_file.exists():
      try:
        with open(self.history_file, "r", encoding="utf-8") as f:
          return json.load(f)
      except Exception:
        return []
    return []

  def _save_history(self):
    """検索履歴の保存"""
    try:
      with open(self.history_file, "w", encoding="utf-8") as f:
        json.dump(self.history[-100:], f, ensure_ascii=False, indent=2)
    except Exception:
      pass

  def parse_query(self, query: str) -> ParsedQuery:
    """
    自然言語クエリを解析

    Args:
      query: 検索クエリ（例：「辛くない簡単な鶏肉料理」）

    Returns:
      ParsedQuery: 解析結果
    """
    query = query.strip()
    original = query

    # 正規化
    query = self._normalize_query(query)

    # 否定表現の抽出
    ingredients_exclude, negations = self._extract_negations(query)

    # 否定部分を除去したクエリ
    query_without_negations = self._remove_negations(query)

    # 各要素の抽出
    ingredients_include = self._extract_ingredients(query_without_negations)
    cooking_methods = self._extract_cooking_methods(query_without_negations)
    categories = self._extract_categories(query_without_negations)
    adjectives = self._extract_adjectives(query_without_negations)

    # キーワード抽出（辞書にない単語）
    keywords = self._extract_keywords(
      query_without_negations,
      ingredients_include + cooking_methods + categories + adjectives
    )

    parsed = ParsedQuery(
      original=original,
      ingredients_include=ingredients_include,
      ingredients_exclude=ingredients_exclude,
      cooking_methods=cooking_methods,
      categories=categories,
      adjectives=adjectives,
      negations=negations,
      keywords=keywords
    )

    # 履歴に追加
    self._add_to_history(parsed)

    return parsed

  def _normalize_query(self, query: str) -> str:
    """クエリの正規化"""
    # 全角→半角スペース
    query = query.replace("　", " ")

    # 同義語の統一
    for standard, synonyms in self.dictionary["synonyms"].items():
      for synonym in synonyms:
        query = query.replace(synonym, standard)

    return query

  def _extract_negations(self, query: str) -> Tuple[List[str], List[str]]:
    """
    否定表現の抽出

    Returns:
      (除外する食材のリスト, 否定表現のリスト)
    """
    exclude_ingredients = []
    negations = []

    # 否定パターンの検出
    for pattern in self.dictionary["negation_patterns"]:
      # 「〇〇ない」「〇〇なし」のパターン
      regex = rf"(\S+?){re.escape(pattern)}"
      matches = re.finditer(regex, query)

      for match in matches:
        base_word = match.group(1)
        full_negation = match.group(0)
        negations.append(full_negation)

        # 食材・調理法・形容詞のチェック
        for ingredient in self.dictionary["ingredients"]:
          if ingredient in base_word:
            exclude_ingredients.append(ingredient)
            break

        for adjective in self.dictionary["adjectives"]:
          if adjective in base_word:
            # 形容詞の否定（例：辛くない → 辛いを除外）
            exclude_ingredients.append(adjective)
            break

    return list(set(exclude_ingredients)), list(set(negations))

  def _remove_negations(self, query: str) -> str:
    """否定表現を除去"""
    for pattern in self.dictionary["negation_patterns"]:
      regex = rf"\S+?{re.escape(pattern)}"
      query = re.sub(regex, "", query)
    return query

  def _extract_ingredients(self, query: str) -> List[str]:
    """食材の抽出"""
    found = []
    for ingredient in self.dictionary["ingredients"]:
      if ingredient in query:
        found.append(ingredient)
    return list(set(found))

  def _extract_cooking_methods(self, query: str) -> List[str]:
    """調理法の抽出"""
    found = []
    for method in self.dictionary["cooking_methods"]:
      if method in query:
        found.append(method)
    return list(set(found))

  def _extract_categories(self, query: str) -> List[str]:
    """カテゴリの抽出"""
    found = []
    for category in self.dictionary["categories"]:
      if category in query:
        found.append(category)
    return list(set(found))

  def _extract_adjectives(self, query: str) -> List[str]:
    """形容詞の抽出"""
    found = []
    for adjective in self.dictionary["adjectives"]:
      if adjective in query:
        found.append(adjective)
    return list(set(found))

  def _extract_keywords(self, query: str, extracted_words: List[str]) -> List[str]:
    """その他キーワードの抽出"""
    # すでに抽出された単語を除去
    for word in extracted_words:
      query = query.replace(word, "")

    # 残った文字列から意味のある単語を抽出
    words = re.findall(r"[\w]+", query)
    keywords = [w for w in words if len(w) >= 2]

    return list(set(keywords))

  def _add_to_history(self, parsed: ParsedQuery):
    """検索履歴に追加"""
    history_item = {
      "query": parsed.original,
      "timestamp": datetime.now().isoformat(),
      "parsed": asdict(parsed)
    }
    self.history.append(history_item)
    self._save_history()

  def get_search_history(self, limit: int = 20) -> List[Dict]:
    """検索履歴の取得"""
    return list(reversed(self.history[-limit:]))

  def get_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
    """
    検索サジェストの取得

    Args:
      partial_query: 入力途中のクエリ
      limit: 最大返却数

    Returns:
      サジェストのリスト
    """
    if not partial_query or len(partial_query) < 1:
      # 人気の検索クエリを返す
      return self._get_popular_queries(limit)

    suggestions = set()
    partial_lower = partial_query.lower()

    # 辞書からマッチする単語を検索
    for category_words in self.dictionary.values():
      if isinstance(category_words, list):
        for word in category_words:
          if word.lower().startswith(partial_lower) or partial_lower in word.lower():
            suggestions.add(word)
            if len(suggestions) >= limit:
              break

    # 履歴からマッチするクエリを検索
    for item in reversed(self.history):
      query = item.get("query", "")
      if partial_lower in query.lower():
        suggestions.add(query)
        if len(suggestions) >= limit:
          break

    return list(suggestions)[:limit]

  def _get_popular_queries(self, limit: int) -> List[str]:
    """人気の検索クエリを取得"""
    # クエリの出現頻度をカウント
    query_counts: Dict[str, int] = {}
    for item in self.history:
      query = item.get("query", "")
      query_counts[query] = query_counts.get(query, 0) + 1

    # 出現頻度順にソート
    sorted_queries = sorted(
      query_counts.items(),
      key=lambda x: x[1],
      reverse=True
    )

    return [q[0] for q in sorted_queries[:limit]]

  def build_search_filters(self, parsed: ParsedQuery) -> Dict:
    """
    解析結果から検索フィルタを構築

    Args:
      parsed: 解析されたクエリ

    Returns:
      検索フィルタの辞書
    """
    filters = {}

    if parsed.ingredients_include:
      filters["ingredients_include"] = parsed.ingredients_include

    if parsed.ingredients_exclude:
      filters["ingredients_exclude"] = parsed.ingredients_exclude

    if parsed.cooking_methods:
      filters["cooking_methods"] = parsed.cooking_methods

    if parsed.categories:
      filters["categories"] = parsed.categories

    if parsed.adjectives:
      filters["adjectives"] = parsed.adjectives

    if parsed.keywords:
      filters["keywords"] = parsed.keywords

    return filters

  def search_recipes(
    self,
    recipes: List[Dict],
    parsed: ParsedQuery
  ) -> List[Dict]:
    """
    レシピを自然言語検索

    Args:
      recipes: レシピのリスト
      parsed: 解析されたクエリ

    Returns:
      マッチしたレシピのリスト（スコア順）
    """
    results = []

    for recipe in recipes:
      score = self._calculate_match_score(recipe, parsed)
      if score > 0:
        results.append({
          "recipe": recipe,
          "score": score
        })

    # スコア順にソート
    results.sort(key=lambda x: x["score"], reverse=True)

    return [r["recipe"] for r in results]

  def _calculate_match_score(self, recipe: Dict, parsed: ParsedQuery) -> float:
    """
    レシピのマッチスコアを計算

    Returns:
      0.0 ～ 100.0 のスコア
    """
    score = 0.0

    # レシピのテキスト情報を結合
    recipe_text = " ".join([
      recipe.get("title", ""),
      recipe.get("description", ""),
      " ".join(recipe.get("ingredients", [])),
      " ".join(recipe.get("steps", [])),
      " ".join(recipe.get("tags", []))
    ]).lower()

    # 食材（含む）のマッチ - 高配点
    for ingredient in parsed.ingredients_include:
      if ingredient.lower() in recipe_text:
        score += 20.0

    # 食材（除く）が含まれている場合はスコアを大幅減点
    for ingredient in parsed.ingredients_exclude:
      if ingredient.lower() in recipe_text:
        score -= 50.0

    # 調理法のマッチ
    for method in parsed.cooking_methods:
      if method.lower() in recipe_text:
        score += 15.0

    # カテゴリのマッチ
    for category in parsed.categories:
      if category.lower() in recipe_text:
        score += 10.0

    # 形容詞のマッチ
    for adjective in parsed.adjectives:
      if adjective.lower() in recipe_text:
        score += 8.0

    # キーワードのマッチ
    for keyword in parsed.keywords:
      if keyword.lower() in recipe_text:
        score += 5.0

    return max(0.0, score)

  def explain_query(self, parsed: ParsedQuery) -> str:
    """
    解析結果を人間が読める形式で説明

    Args:
      parsed: 解析されたクエリ

    Returns:
      説明文
    """
    parts = []

    if parsed.ingredients_include:
      parts.append(f"食材: {', '.join(parsed.ingredients_include)}")

    if parsed.ingredients_exclude:
      parts.append(f"除外: {', '.join(parsed.ingredients_exclude)}")

    if parsed.cooking_methods:
      parts.append(f"調理法: {', '.join(parsed.cooking_methods)}")

    if parsed.categories:
      parts.append(f"カテゴリ: {', '.join(parsed.categories)}")

    if parsed.adjectives:
      parts.append(f"特徴: {', '.join(parsed.adjectives)}")

    if parsed.keywords:
      parts.append(f"キーワード: {', '.join(parsed.keywords)}")

    if not parts:
      return "検索条件なし"

    return " | ".join(parts)
