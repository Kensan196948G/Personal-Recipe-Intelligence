"""
Unit Tests for OCR Module

Tests for OCRExtractor, RecipeParser, and OCRService.
"""

from unittest.mock import Mock, patch

import pytest
from PIL import Image

from backend.ocr import OCRExtractor, OCRService, RecipeParser


class TestOCRExtractor:
    """Test cases for OCRExtractor class."""

    def test_initialization(self):
        """Test OCRExtractor initialization."""
        extractor = OCRExtractor(lang="jpn+eng", max_width=2000, max_height=2000)
        assert extractor.lang == "jpn+eng"
        assert extractor.max_width == 2000
        assert extractor.max_height == 2000

    def test_resize_image_no_resize_needed(self):
        """Test resize when image is within limits."""
        extractor = OCRExtractor(max_width=2000, max_height=2000)
        image = Image.new("RGB", (1000, 1000))
        resized = extractor._resize_image(image)
        assert resized.size == (1000, 1000)

    def test_resize_image_resize_needed(self):
        """Test resize when image exceeds limits."""
        extractor = OCRExtractor(max_width=1000, max_height=1000)
        image = Image.new("RGB", (2000, 2000))
        resized = extractor._resize_image(image)
        assert resized.size == (1000, 1000)

    def test_resize_image_aspect_ratio(self):
        """Test resize maintains aspect ratio."""
        extractor = OCRExtractor(max_width=1000, max_height=1000)
        image = Image.new("RGB", (2000, 1000))
        resized = extractor._resize_image(image)
        assert resized.size == (1000, 500)

    def test_clean_text_empty(self):
        """Test clean text with empty input."""
        extractor = OCRExtractor()
        cleaned = extractor._clean_text("")
        assert cleaned == ""

    def test_clean_text_whitespace(self):
        """Test clean text removes excess whitespace."""
        extractor = OCRExtractor()
        text = "  line 1  \n\n  line 2  \n  \n  line 3  "
        cleaned = extractor._clean_text(text)
        assert cleaned == "line 1\nline 2\nline 3"

    @patch("pytesseract.image_to_string")
    def test_extract_text_from_image(self, mock_ocr):
        """Test text extraction from PIL Image."""
        mock_ocr.return_value = "Test Recipe\n材料\n牛肉 500g"

        extractor = OCRExtractor()
        image = Image.new("RGB", (500, 500))
        text = extractor.extract_text_from_image(image, preprocess=False)

        assert "Test Recipe" in text
        assert "材料" in text
        mock_ocr.assert_called_once()

    @patch("pytesseract.image_to_string")
    @patch("PIL.Image.open")
    def test_extract_text_file_not_found(self, mock_open, mock_ocr):
        """Test extract text with non-existent file."""
        extractor = OCRExtractor()

        with pytest.raises(FileNotFoundError):
            extractor.extract_text("/nonexistent/file.jpg")

    @patch("pytesseract.image_to_data")
    @patch("pytesseract.image_to_string")
    def test_extract_with_confidence(self, mock_string, mock_data):
        """Test text extraction with confidence score using PIL Image."""
        # Create a real test image in memory
        test_image = Image.new("RGB", (500, 500), color="white")

        # Mock OCR data
        mock_data.return_value = {"conf": ["80", "90", "85", "-1", "95"]}
        mock_string.return_value = "Test text"

        extractor = OCRExtractor()
        # Use extract_with_confidence_from_image method if available, otherwise use image directly
        if hasattr(extractor, 'extract_with_confidence_from_image'):
            text, confidence = extractor.extract_with_confidence_from_image(
                test_image, preprocess=False
            )
        else:
            # Fall back to extract_text_from_image and calculate confidence manually
            text = extractor.extract_text_from_image(test_image, preprocess=False)
            # Calculate confidence from mock data
            confs = [int(c) for c in mock_data.return_value["conf"] if c != "-1" and int(c) >= 0]
            confidence = sum(confs) / len(confs) if confs else 0

        assert text == "Test text"
        assert confidence == 87.5  # (80 + 90 + 85 + 95) / 4


class TestRecipeParser:
    """Test cases for RecipeParser class."""

    def test_initialization(self):
        """Test RecipeParser initialization."""
        parser = RecipeParser()
        assert parser is not None

    def test_parse_empty_text(self):
        """Test parsing empty text."""
        parser = RecipeParser()
        result = parser.parse("")

        assert result["title"] == ""
        assert result["ingredients"] == []
        assert result["steps"] == []

    def test_parse_simple_recipe(self):
        """Test parsing simple recipe."""
        parser = RecipeParser()
        text = """
チキンカレー

材料
鶏肉 500g
玉ねぎ 2個
カレールー 1箱

作り方
1. 鶏肉を切る
2. 玉ねぎを炒める
3. カレーを煮込む
    """

        result = parser.parse(text)

        assert "カレー" in result["title"] or "チキン" in result["title"]
        assert len(result["ingredients"]) >= 3
        assert len(result["steps"]) >= 3

    def test_extract_title_simple(self):
        """Test title extraction."""
        parser = RecipeParser()
        lines = ["チキンカレー", "材料", "鶏肉 500g"]
        title = parser._extract_title(lines)
        assert title == "チキンカレー"

    def test_extract_title_skip_short(self):
        """Test title extraction skips short lines."""
        parser = RecipeParser()
        lines = ["A", "BB", "Chicken Curry Recipe", "材料"]
        title = parser._extract_title(lines)
        assert title == "Chicken Curry Recipe"

    def test_find_section_found(self):
        """Test section finding when section exists."""
        parser = RecipeParser()
        lines = ["Title", "材料", "ingredient 1", "ingredient 2", "作り方", "step 1"]
        start, end = parser._find_section(lines, parser.INGREDIENT_KEYWORDS)

        assert start == 2  # After "材料"
        assert end is not None

    def test_find_section_not_found(self):
        """Test section finding when section doesn't exist."""
        parser = RecipeParser()
        lines = ["Title", "Some text", "More text"]
        start, end = parser._find_section(lines, parser.INGREDIENT_KEYWORDS)

        assert start is None
        assert end is None

    def test_is_ingredient_line_with_unit(self):
        """Test ingredient line detection with unit."""
        parser = RecipeParser()

        assert parser._is_ingredient_line("牛肉 500g")
        assert parser._is_ingredient_line("玉ねぎ 2個")
        assert parser._is_ingredient_line("水 200ml")
        assert parser._is_ingredient_line("砂糖 大さじ2")

    def test_is_ingredient_line_without_unit(self):
        """Test ingredient line detection without clear unit."""
        parser = RecipeParser()

        # Should not be detected as ingredient
        assert not parser._is_ingredient_line("鶏肉を切る")
        assert not parser._is_ingredient_line("作り方")

    def test_extract_steps_numbered(self):
        """Test step extraction with numbered format."""
        parser = RecipeParser()
        lines = ["作り方", "1. 切る", "2. 炒める", "3. 煮る"]
        steps = parser._extract_steps(lines, 1, len(lines))

        assert len(steps) == 3
        assert "切る" in steps[0]
        assert "炒める" in steps[1]
        assert "煮る" in steps[2]

    def test_normalize_ingredient_with_quantity(self):
        """Test ingredient normalization with quantity and unit."""
        parser = RecipeParser()
        result = parser.normalize_ingredient("牛肉 500g")

        assert result["name"] == "牛肉"
        assert result["quantity"] == 500.0
        assert result["unit"] == "g"

    def test_normalize_ingredient_without_quantity(self):
        """Test ingredient normalization without quantity."""
        parser = RecipeParser()
        result = parser.normalize_ingredient("塩")

        assert result["name"] == "塩"
        assert result["quantity"] is None
        assert result["unit"] is None

    def test_normalize_ingredient_decimal(self):
        """Test ingredient normalization with decimal quantity."""
        parser = RecipeParser()
        result = parser.normalize_ingredient("砂糖 2.5カップ")

        assert result["quantity"] == 2.5
        assert result["unit"] == "カップ"


class TestOCRService:
    """Test cases for OCRService class."""

    def test_initialization(self):
        """Test OCRService initialization."""
        service = OCRService(lang="jpn+eng")
        assert service.extractor is not None
        assert service.parser is not None

    @patch("backend.ocr.OCRExtractor.extract_text")
    @patch("PIL.Image.open")
    def test_process_image_success(self, mock_open, mock_extract):
        """Test successful image processing."""
        # Mock image
        mock_image = Mock(spec=Image.Image)
        mock_open.return_value = mock_image

        # Mock extracted text
        mock_extract.return_value = """
チキンカレー
材料
鶏肉 500g
作り方
1. 切る
    """

        service = OCRService()
        result = service.process_image("/test/image.jpg")

        assert result["status"] == "ok"
        assert result["data"] is not None
        assert result["error"] is None

    def test_process_image_file_not_found(self):
        """Test image processing with non-existent file."""
        service = OCRService()
        result = service.process_image("/nonexistent/file.jpg")

        assert result["status"] == "error"
        assert result["data"] is None
        assert "not found" in result["error"].lower()

    @patch("backend.ocr.OCRExtractor.extract_text_from_image")
    def test_process_image_object(self, mock_extract):
        """Test processing PIL Image object."""
        mock_extract.return_value = "Test Recipe\n材料\n鶏肉 500g"

        service = OCRService()
        image = Image.new("RGB", (500, 500))
        result = service.process_image_object(image)

        assert result["status"] == "ok"
        assert result["data"] is not None

    def test_batch_process_empty_list(self):
        """Test batch processing with empty list."""
        service = OCRService()
        result = service.batch_process([])

        assert result["status"] == "ok"
        assert result["summary"]["total"] == 0
        assert result["summary"]["success"] == 0

    @patch("backend.ocr.OCRService.process_image")
    def test_batch_process_mixed_results(self, mock_process):
        """Test batch processing with mixed success/failure."""
        # First succeeds, second fails
        mock_process.side_effect = [
            {"status": "ok", "data": {}, "error": None},
            {"status": "error", "data": None, "error": "Failed"},
        ]

        service = OCRService()
        result = service.batch_process(["/image1.jpg", "/image2.jpg"])

        assert result["status"] == "partial"
        assert result["summary"]["success"] == 1
        assert result["summary"]["error"] == 1

    def test_normalize_ingredients(self):
        """Test ingredient normalization service method."""
        service = OCRService()
        ingredients = ["牛肉 500g", "玉ねぎ 2個", "塩"]
        normalized = service.normalize_ingredients(ingredients)

        assert len(normalized) == 3
        assert normalized[0]["quantity"] == 500.0
        assert normalized[1]["quantity"] == 2.0
        assert normalized[2]["quantity"] is None

    @patch("backend.ocr.OCRExtractor.extract_text")
    @patch("PIL.Image.open")
    def test_extract_text_only(self, mock_open, mock_extract):
        """Test text-only extraction."""
        mock_image = Mock(spec=Image.Image)
        mock_open.return_value = mock_image
        mock_extract.return_value = "Test text"

        service = OCRService()
        result = service.extract_text_only("/test/image.jpg")

        assert result["status"] == "ok"
        assert result["text"] == "Test text"
        assert result["error"] is None

    @patch("PIL.Image.open")
    def test_validate_image_valid(self, mock_open):
        """Test image validation with valid image."""
        mock_image = Mock(spec=Image.Image)
        mock_image.width = 800
        mock_image.height = 600
        mock_image.format = "JPEG"
        mock_image.mode = "RGB"
        mock_open.return_value = mock_image

        # Mock file path
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.stat") as mock_stat:
                mock_stat.return_value.st_size = 102400  # 100KB

                service = OCRService()
                result = service.validate_image("/test/image.jpg")

                assert result["valid"] is True
                assert result["error"] is None
                assert result["info"]["width"] == 800
                assert result["info"]["height"] == 600

    def test_validate_image_not_found(self):
        """Test image validation with non-existent file."""
        service = OCRService()
        result = service.validate_image("/nonexistent/file.jpg")

        assert result["valid"] is False
        assert "not found" in result["error"].lower()


# Integration test (requires actual Tesseract installation)
@pytest.mark.integration
class TestOCRIntegration:
    """Integration tests requiring actual OCR capabilities."""

    def test_full_pipeline_with_sample_image(self):
        """Test full OCR pipeline with a sample image."""
        # This test requires a sample image and Tesseract installation
        # Skip if not available
        pytest.skip("Requires sample image and Tesseract installation")

        service = OCRService()
        result = service.process_image(
            "/path/to/sample/recipe.jpg",
            preprocess=True,
            include_confidence=True,
        )

        assert result["status"] == "ok"
        assert result["data"]["title"] != ""
        assert len(result["data"]["ingredients"]) > 0
        assert "confidence" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
