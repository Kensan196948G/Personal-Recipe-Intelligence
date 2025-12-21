"""
OCR Module for Personal Recipe Intelligence

This module provides OCR capabilities for extracting recipe data from images.

Main components:
- OCRExtractor: Image preprocessing and text extraction
- RecipeParser: Parse OCR text into structured recipe data
- OCRService: High-level service combining extraction and parsing
"""

from .extractor import OCRExtractor
from .parser import RecipeParser
from .service import OCRService

__all__ = [
    "OCRExtractor",
    "RecipeParser",
    "OCRService",
]
