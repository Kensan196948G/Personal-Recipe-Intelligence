"""
Scraper API Router - Web recipe scraping endpoints
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from backend.api.schemas import ApiResponse
from backend.core.database import get_session

router = APIRouter(prefix="/api/v1/scraper", tags=["scraper"])


class ScrapeRequest(BaseModel):
    """スクレイピングリクエスト"""

    url: HttpUrl = Field(..., description="レシピページのURL")
    save: bool = Field(default=False, description="スクレイピング後に保存するか")


class ScrapeResult(BaseModel):
    """スクレイピング結果"""

    title: str
    description: Optional[str] = None
    servings: Optional[int] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    ingredients: list[dict] = Field(default_factory=list)
    steps: list[dict] = Field(default_factory=list)
    source_url: str
    source_type: str = "web"


@router.post("/scrape", response_model=ApiResponse)
async def scrape_recipe(request: ScrapeRequest, session=Depends(get_session)):
    """URLからレシピをスクレイピング"""
    try:
        from backend.scraper import CookpadScraper, DelishKitchenScraper, GenericScraper

        url_str = str(request.url)

        # サイトに応じたスクレイパーを選択
        if "cookpad.com" in url_str:
            scraper = CookpadScraper()
        elif "delishkitchen.tv" in url_str:
            scraper = DelishKitchenScraper()
        else:
            scraper = GenericScraper()

        # スクレイピング実行
        result = await scraper.scrape(url_str)

        if not result:
            raise HTTPException(status_code=400, detail="レシピの抽出に失敗しました")

        # 保存オプション
        if request.save:
            from backend.services.recipe_service import RecipeService

            service = RecipeService(session)
            recipe = service.create_recipe(
                title=result.get("title", "無題のレシピ"),
                description=result.get("description"),
                servings=result.get("servings"),
                prep_time_minutes=result.get("prep_time_minutes"),
                cook_time_minutes=result.get("cook_time_minutes"),
                source_url=url_str,
                source_type="web",
                ingredients=result.get("ingredients", []),
                steps=result.get("steps", []),
            )
            return ApiResponse(
                status="ok",
                data={
                    "message": "レシピを保存しました",
                    "recipe_id": recipe.id,
                    "recipe": result,
                },
            )

        return ApiResponse(status="ok", data=result)

    except ImportError:
        raise HTTPException(
            status_code=501, detail="スクレイパーモジュールが利用できません"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-sites", response_model=ApiResponse)
async def get_supported_sites():
    """サポートされているサイト一覧"""
    sites = [
        {"name": "Cookpad", "domain": "cookpad.com", "status": "supported"},
        {"name": "Delish Kitchen", "domain": "delishkitchen.tv", "status": "supported"},
        {"name": "その他", "domain": "*", "status": "generic"},
    ]
    return ApiResponse(status="ok", data=sites)
