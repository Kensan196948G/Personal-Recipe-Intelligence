"""
OCR Module - Image-to-recipe extraction functionality

Provides OCR capabilities for extracting recipes from images:
- OCRExtractor: Text extraction from images using pytesseract
- RecipeParser: Parse extracted text into structured recipe data
- OCRService: High-level service for complete OCR workflow
"""

from backend.ocr.extractor import OCRExtractor
from backend.ocr.parser import RecipeParser
from backend.ocr.service import OCRService

__all__ = [
  "OCRExtractor",
  "RecipeParser",
  "OCRService",
]
