"""
Natural Search Router
自然言語検索用 API ルーター
"""

from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime

from backend.services.natural_search_service import NaturalSearchService
from backend.services.recipe_service import RecipeService


router = APIRouter(prefix="/api/v1/ai/search", tags=["natural-search"])

# サービスのインスタンス
natural_search_service = NaturalSearchService()
recipe_service = RecipeService()


class NaturalSearchRequest(BaseModel):
    """自然言語検索リクエスト"""

    query: str = Field(..., min_length=1, max_length=200, description="検索クエリ")
    limit: Optional[int] = Field(20, ge=1, le=100, description="最大返却数")


class ParseQueryRequest(BaseModel):
    """クエリ解析リクエスト"""

    query: str = Field(..., min_length=1, max_length=200, description="検索クエリ")


class ParsedQueryResponse(BaseModel):
    """解析結果レスポンス"""

    original: str
    ingredients_include: List[str]
    ingredients_exclude: List[str]
    cooking_methods: List[str]
    categories: List[str]
    adjectives: List[str]
    negations: List[str]
    keywords: List[str]
    explanation: str


class SearchResultResponse(BaseModel):
    """検索結果レスポンス"""

    query: str
    parsed: ParsedQueryResponse
    results: List[Dict]
    total: int
    timestamp: str


class SuggestionResponse(BaseModel):
    """サジェストレスポンス"""

    suggestions: List[str]


class HistoryItemResponse(BaseModel):
    """履歴アイテム"""

    query: str
    timestamp: str
    parsed: Dict


class HistoryResponse(BaseModel):
    """履歴レスポンス"""

    history: List[HistoryItemResponse]
    total: int


@router.post("/", response_model=SearchResultResponse)
async def natural_search(request: NaturalSearchRequest):
    """
    自然言語検索

    日本語の自然な表現で料理を検索します。

    例:
    - 「辛くない簡単な鶏肉料理」
    - 「ヘルシーな野菜たっぷりサラダ」
    - 「時短でできるパスタ」
    """
    try:
        # クエリ解析
        parsed = natural_search_service.parse_query(request.query)

        # レシピ取得
        all_recipes = recipe_service.get_all_recipes()

        # 検索実行
        results = natural_search_service.search_recipes(all_recipes, parsed)

        # 件数制限
        limited_results = results[: request.limit]

        # 説明文生成
        explanation = natural_search_service.explain_query(parsed)

        return SearchResultResponse(
            query=request.query,
            parsed=ParsedQueryResponse(
                original=parsed.original,
                ingredients_include=parsed.ingredients_include,
                ingredients_exclude=parsed.ingredients_exclude,
                cooking_methods=parsed.cooking_methods,
                categories=parsed.categories,
                adjectives=parsed.adjectives,
                negations=parsed.negations,
                keywords=parsed.keywords,
                explanation=explanation,
            ),
            results=limited_results,
            total=len(results),
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"検索エラー: {str(e)}")


@router.post("/parse", response_model=ParsedQueryResponse)
async def parse_query(request: ParseQueryRequest):
    """
    クエリ解析のみ実行

    検索は実行せず、クエリの解析結果のみを返します。
    デバッグや解析結果のプレビューに使用できます。
    """
    try:
        parsed = natural_search_service.parse_query(request.query)
        explanation = natural_search_service.explain_query(parsed)

        return ParsedQueryResponse(
            original=parsed.original,
            ingredients_include=parsed.ingredients_include,
            ingredients_exclude=parsed.ingredients_exclude,
            cooking_methods=parsed.cooking_methods,
            categories=parsed.categories,
            adjectives=parsed.adjectives,
            negations=parsed.negations,
            keywords=parsed.keywords,
            explanation=explanation,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析エラー: {str(e)}")


@router.get("/suggestions", response_model=SuggestionResponse)
async def get_suggestions(
    q: str = Query("", description="部分クエリ"),
    limit: int = Query(10, ge=1, le=50, description="最大返却数"),
):
    """
    検索サジェスト取得

    入力途中のクエリに対してサジェストを返します。
    クエリが空の場合は人気の検索クエリを返します。
    """
    try:
        suggestions = natural_search_service.get_suggestions(q, limit)

        return SuggestionResponse(suggestions=suggestions)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サジェスト取得エラー: {str(e)}")


@router.get("/history", response_model=HistoryResponse)
async def get_history(limit: int = Query(20, ge=1, le=100, description="最大返却数")):
    """
    検索履歴取得

    過去の検索クエリと解析結果を返します。
    """
    try:
        history = natural_search_service.get_search_history(limit)

        history_items = [
            HistoryItemResponse(
                query=item["query"], timestamp=item["timestamp"], parsed=item["parsed"]
            )
            for item in history
        ]

        return HistoryResponse(history=history_items, total=len(history_items))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"履歴取得エラー: {str(e)}")


@router.delete("/history")
async def clear_history():
    """
    検索履歴クリア

    すべての検索履歴を削除します。
    """
    try:
        natural_search_service.history = []
        natural_search_service._save_history()

        return {"status": "ok", "message": "検索履歴をクリアしました"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"履歴削除エラー: {str(e)}")
