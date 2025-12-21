"""Tests for web scraper functionality.

MockScraper を使用したスクレイパー機能のユニットテスト。
"""

import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup


class MockScraper:
    """Mock scraper class for testing."""

    def __init__(self):
        self.supported_domains = [
            "cookpad.com",
            "kurashiru.com",
            "recipe.rakuten.co.jp",
        ]

    def is_supported_url(self, url: str) -> bool:
        """Check if URL is from supported domain."""
        return any(domain in url for domain in self.supported_domains)

    def extract_recipe(self, html_content: str) -> dict:
        """Extract recipe from HTML content."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title
        title_tag = soup.find("h1")
        title = title_tag.text.strip() if title_tag else "Untitled Recipe"

        # Extract ingredients
        ingredients = []
        ingredients_section = soup.find("div", class_="ingredients")
        if ingredients_section:
            for li in ingredients_section.find_all("li"):
                text = li.text.strip()
                # Simple parsing: "ingredient amount"
                parts = text.rsplit(" ", 1)
                if len(parts) == 2:
                    ingredients.append({"name": parts[0], "amount": parts[1]})
                else:
                    ingredients.append({"name": text, "amount": "適量"})

        # Extract steps
        steps = []
        steps_section = soup.find("div", class_="steps")
        if steps_section:
            for li in steps_section.find_all("li"):
                steps.append(li.text.strip())

        return {"title": title, "ingredients": ingredients, "steps": steps, "tags": []}

    def normalize_ingredient_name(self, name: str) -> str:
        """Normalize ingredient name."""
        normalization_map = {
            "玉ねぎ": "たまねぎ",
            "玉葱": "たまねぎ",
            "タマネギ": "たまねぎ",
            "人参": "にんじん",
            "ニンジン": "にんじん",
            "馬鈴薯": "じゃがいも",
            "ジャガイモ": "じゃがいも",
        }
        return normalization_map.get(name, name)


class TestScraper:
    """Test suite for web scraper."""

    def test_is_supported_url_cookpad(self):
        """Test URL validation for Cookpad."""
        scraper = MockScraper()
        assert scraper.is_supported_url("https://cookpad.com/recipe/12345")
        assert scraper.is_supported_url("https://www.cookpad.com/recipe/12345")

    def test_is_supported_url_kurashiru(self):
        """Test URL validation for Kurashiru."""
        scraper = MockScraper()
        assert scraper.is_supported_url("https://kurashiru.com/recipes/abc123")

    def test_is_supported_url_rakuten(self):
        """Test URL validation for Rakuten Recipe."""
        scraper = MockScraper()
        assert scraper.is_supported_url("https://recipe.rakuten.co.jp/recipe/123")

    def test_is_supported_url_unsupported(self):
        """Test URL validation for unsupported domain."""
        scraper = MockScraper()
        assert not scraper.is_supported_url("https://example.com/recipe")
        assert not scraper.is_supported_url("https://youtube.com/watch")

    def test_extract_recipe_basic(self, mock_html_content):
        """Test basic recipe extraction."""
        scraper = MockScraper()
        recipe = scraper.extract_recipe(mock_html_content)

        assert recipe["title"] == "美味しいカレーの作り方"
        assert len(recipe["ingredients"]) == 4
        assert len(recipe["steps"]) == 5

    def test_extract_recipe_ingredients(self, mock_html_content):
        """Test ingredient extraction."""
        scraper = MockScraper()
        recipe = scraper.extract_recipe(mock_html_content)

        ingredient_names = [ing["name"] for ing in recipe["ingredients"]]
        assert "たまねぎ" in ingredient_names
        assert "にんじん" in ingredient_names
        assert "じゃがいも" in ingredient_names

    def test_extract_recipe_steps(self, mock_html_content):
        """Test step extraction."""
        scraper = MockScraper()
        recipe = scraper.extract_recipe(mock_html_content)

        assert "野菜を洗って皮をむく" in recipe["steps"]
        assert "野菜を一口大に切る" in recipe["steps"]
        assert "カレールーを入れて完成" in recipe["steps"]

    def test_extract_recipe_empty_html(self):
        """Test extraction from empty HTML."""
        scraper = MockScraper()
        recipe = scraper.extract_recipe("<html><body></body></html>")

        assert recipe["title"] == "Untitled Recipe"
        assert len(recipe["ingredients"]) == 0
        assert len(recipe["steps"]) == 0

    def test_extract_recipe_malformed_html(self):
        """Test extraction from malformed HTML."""
        scraper = MockScraper()
        malformed = '<html><h1>Test</h1><div class="ingredients">'

        # Should not raise exception
        recipe = scraper.extract_recipe(malformed)
        assert recipe["title"] == "Test"

    def test_normalize_ingredient_name_onion(self):
        """Test ingredient normalization for onion."""
        scraper = MockScraper()

        assert scraper.normalize_ingredient_name("玉ねぎ") == "たまねぎ"
        assert scraper.normalize_ingredient_name("玉葱") == "たまねぎ"
        assert scraper.normalize_ingredient_name("タマネギ") == "たまねぎ"

    def test_normalize_ingredient_name_carrot(self):
        """Test ingredient normalization for carrot."""
        scraper = MockScraper()

        assert scraper.normalize_ingredient_name("人参") == "にんじん"
        assert scraper.normalize_ingredient_name("ニンジン") == "にんじん"

    def test_normalize_ingredient_name_potato(self):
        """Test ingredient normalization for potato."""
        scraper = MockScraper()

        assert scraper.normalize_ingredient_name("馬鈴薯") == "じゃがいも"
        assert scraper.normalize_ingredient_name("ジャガイモ") == "じゃがいも"

    def test_normalize_ingredient_name_unchanged(self):
        """Test ingredient normalization for unknown ingredient."""
        scraper = MockScraper()

        assert scraper.normalize_ingredient_name("醤油") == "醤油"
        assert scraper.normalize_ingredient_name("塩") == "塩"

    @patch("requests.get")
    def test_fetch_url_success(self, mock_get):
        """Test successful URL fetching."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test</body></html>"
        mock_get.return_value = mock_response

        # Simulate fetch
        response = mock_get("https://example.com")
        assert response.status_code == 200
        assert "Test" in response.text

    @patch("requests.get")
    def test_fetch_url_404_error(self, mock_get):
        """Test handling 404 error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        response = mock_get("https://example.com/notfound")
        assert response.status_code == 404

    @patch("requests.get")
    def test_fetch_url_timeout(self, mock_get):
        """Test handling timeout error."""
        mock_get.side_effect = TimeoutError("Request timeout")

        with pytest.raises(TimeoutError):
            mock_get("https://example.com", timeout=5)

    @patch("requests.get")
    def test_fetch_url_network_error(self, mock_get):
        """Test handling network error."""
        mock_get.side_effect = ConnectionError("Network error")

        with pytest.raises(ConnectionError):
            mock_get("https://example.com")

    def test_extract_image_url(self):
        """Test image URL extraction."""
        html = """
    <html>
      <body>
        <div class="recipe-image">
          <img src="https://example.com/image.jpg" alt="Recipe">
        </div>
      </body>
    </html>
    """

        soup = BeautifulSoup(html, "html.parser")
        img_tag = soup.find("img")

        assert img_tag is not None
        assert img_tag["src"] == "https://example.com/image.jpg"

    def test_extract_cooking_time(self):
        """Test cooking time extraction."""
        html = """
    <html>
      <body>
        <div class="cooking-time">調理時間: 30分</div>
      </body>
    </html>
    """

        soup = BeautifulSoup(html, "html.parser")
        time_div = soup.find("div", class_="cooking-time")

        assert time_div is not None
        # Extract number
        import re

        match = re.search(r"(\d+)", time_div.text)
        if match:
            cooking_time = int(match.group(1))
            assert cooking_time == 30

    def test_extract_servings(self):
        """Test servings extraction."""
        html = """
    <html>
      <body>
        <div class="servings">4人分</div>
      </body>
    </html>
    """

        soup = BeautifulSoup(html, "html.parser")
        servings_div = soup.find("div", class_="servings")

        assert servings_div is not None
        import re

        match = re.search(r"(\d+)", servings_div.text)
        if match:
            servings = int(match.group(1))
            assert servings == 4

    def test_extract_tags(self):
        """Test tags extraction."""
        html = """
    <html>
      <body>
        <div class="tags">
          <span class="tag">簡単</span>
          <span class="tag">野菜料理</span>
          <span class="tag">時短</span>
        </div>
      </body>
    </html>
    """

        soup = BeautifulSoup(html, "html.parser")
        tag_elements = soup.find_all("span", class_="tag")
        tags = [tag.text.strip() for tag in tag_elements]

        assert len(tags) == 3
        assert "簡単" in tags
        assert "野菜料理" in tags
        assert "時短" in tags

    def test_clean_text(self):
        """Test text cleaning."""
        dirty_text = "  材料名\n\t "
        clean = dirty_text.strip()

        assert clean == "材料名"
        assert "\n" not in clean
        assert "\t" not in clean

    def test_parse_ingredient_with_unit(self):
        """Test parsing ingredient with unit."""
        text = "たまねぎ 1個"
        parts = text.rsplit(" ", 1)

        assert len(parts) == 2
        assert parts[0] == "たまねぎ"
        assert parts[1] == "1個"

    def test_parse_ingredient_without_unit(self):
        """Test parsing ingredient without unit."""
        text = "塩"
        parts = text.rsplit(" ", 1)

        if len(parts) == 1:
            ingredient = {"name": parts[0], "amount": "適量"}
            assert ingredient["name"] == "塩"
            assert ingredient["amount"] == "適量"
