"""
OCR Module Configuration

Configuration settings for OCR processing, including language settings,
image processing parameters, and parsing rules.
"""

import os
from typing import Dict, List


class OCRConfig:
  """OCR module configuration."""

  # Language Settings
  DEFAULT_LANGUAGE = "jpn+eng"  # Japanese + English
  SUPPORTED_LANGUAGES = [
    "jpn",  # Japanese
    "eng",  # English
    "chi_sim",  # Chinese Simplified
    "chi_tra",  # Chinese Traditional
    "kor",  # Korean
    "jpn+eng",  # Japanese + English
  ]

  # Image Processing
  MAX_IMAGE_WIDTH = int(os.getenv("OCR_MAX_WIDTH", "2000"))
  MAX_IMAGE_HEIGHT = int(os.getenv("OCR_MAX_HEIGHT", "2000"))
  PREPROCESSING_ENABLED = os.getenv("OCR_PREPROCESS", "true").lower() == "true"

  # Tesseract Configuration
  TESSERACT_CMD = os.getenv("TESSERACT_CMD", "tesseract")
  TESSERACT_PSM = int(os.getenv("TESSERACT_PSM", "6"))  # Page segmentation mode

  # OCR Quality Settings
  MIN_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_MIN_CONFIDENCE", "50.0"))
  ENABLE_CONFIDENCE_CHECK = os.getenv("OCR_CHECK_CONFIDENCE", "false").lower() == "true"

  # Image Preprocessing Parameters
  DENOISE_STRENGTH = int(os.getenv("OCR_DENOISE_STRENGTH", "10"))
  CLAHE_CLIP_LIMIT = float(os.getenv("OCR_CLAHE_CLIP", "2.0"))
  CLAHE_TILE_SIZE = int(os.getenv("OCR_CLAHE_TILE", "8"))

  # Performance
  BATCH_SIZE = int(os.getenv("OCR_BATCH_SIZE", "10"))
  ENABLE_PARALLEL_PROCESSING = os.getenv("OCR_PARALLEL", "false").lower() == "true"
  MAX_WORKERS = int(os.getenv("OCR_MAX_WORKERS", "4"))


class ParserConfig:
  """Recipe parser configuration."""

  # Section Keywords (Japanese)
  INGREDIENT_KEYWORDS_JPN: List[str] = [
    "材料",
    "材料名",
    "用意するもの",
    "必要なもの",
    "ingredient",
  ]

  # Section Keywords (English)
  INGREDIENT_KEYWORDS_ENG: List[str] = [
    "ingredients",
    "ingredient",
    "materials",
    "what you need",
  ]

  # Steps Keywords (Japanese)
  STEPS_KEYWORDS_JPN: List[str] = [
    "作り方",
    "手順",
    "調理手順",
    "調理方法",
    "レシピ",
  ]

  # Steps Keywords (English)
  STEPS_KEYWORDS_ENG: List[str] = [
    "instructions",
    "directions",
    "steps",
    "method",
    "procedure",
    "how to make",
  ]

  # Combined keywords
  INGREDIENT_KEYWORDS = INGREDIENT_KEYWORDS_JPN + INGREDIENT_KEYWORDS_ENG
  STEPS_KEYWORDS = STEPS_KEYWORDS_JPN + STEPS_KEYWORDS_ENG

  # Measurement Units (Japanese)
  UNITS_JPN: List[str] = [
    "g",
    "kg",
    "ml",
    "l",
    "cc",
    "カップ",
    "個",
    "本",
    "枚",
    "切れ",
    "片",
    "大さじ",
    "小さじ",
    "適量",
    "少々",
  ]

  # Measurement Units (English)
  UNITS_ENG: List[str] = [
    "g",
    "kg",
    "ml",
    "l",
    "cup",
    "cups",
    "tbsp",
    "tsp",
    "oz",
    "lb",
    "piece",
    "pieces",
  ]

  # Combined units
  MEASUREMENT_UNITS = list(set(UNITS_JPN + UNITS_ENG))

  # Parsing Rules
  MIN_TITLE_LENGTH = int(os.getenv("PARSER_MIN_TITLE_LEN", "3"))
  MAX_TITLE_LENGTH = int(os.getenv("PARSER_MAX_TITLE_LEN", "100"))
  MIN_INGREDIENT_LENGTH = int(os.getenv("PARSER_MIN_INGREDIENT_LEN", "2"))
  MIN_STEP_LENGTH = int(os.getenv("PARSER_MIN_STEP_LEN", "5"))

  # OCR Error Correction
  ENABLE_ERROR_CORRECTION = os.getenv("PARSER_ERROR_CORRECTION", "true").lower() == "true"

  # Common OCR errors (character substitutions)
  OCR_ERROR_MAP: Dict[str, str] = {
    "O": "0",  # Letter O to zero
    "l": "1",  # Lowercase L to one
    "I": "1",  # Uppercase I to one
    "S": "5",  # Sometimes S is misread as 5
    "B": "8",  # Sometimes B is misread as 8
  }


class ServiceConfig:
  """OCR Service configuration."""

  # Default settings
  DEFAULT_LANG = OCRConfig.DEFAULT_LANGUAGE
  DEFAULT_PREPROCESS = OCRConfig.PREPROCESSING_ENABLED
  DEFAULT_INCLUDE_CONFIDENCE = False

  # Batch processing
  MAX_BATCH_SIZE = int(os.getenv("SERVICE_MAX_BATCH", "50"))
  BATCH_TIMEOUT_SECONDS = int(os.getenv("SERVICE_BATCH_TIMEOUT", "300"))

  # File validation
  SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]
  MAX_FILE_SIZE_MB = int(os.getenv("SERVICE_MAX_FILE_SIZE", "10"))

  # Logging
  LOG_LEVEL = os.getenv("OCR_LOG_LEVEL", "INFO")
  LOG_OCR_TEXT = os.getenv("LOG_OCR_TEXT", "false").lower() == "true"
  LOG_PARSE_RESULTS = os.getenv("LOG_PARSE_RESULTS", "true").lower() == "true"


# Environment-specific configurations
class DevelopmentConfig:
  """Development environment configuration."""

  DEBUG = True
  LOG_LEVEL = "DEBUG"
  ENABLE_CONFIDENCE_CHECK = True
  LOG_OCR_TEXT = True
  LOG_PARSE_RESULTS = True


class ProductionConfig:
  """Production environment configuration."""

  DEBUG = False
  LOG_LEVEL = "INFO"
  ENABLE_CONFIDENCE_CHECK = True
  LOG_OCR_TEXT = False
  LOG_PARSE_RESULTS = False


class TestingConfig:
  """Testing environment configuration."""

  DEBUG = True
  LOG_LEVEL = "DEBUG"
  ENABLE_CONFIDENCE_CHECK = False
  LOG_OCR_TEXT = True
  LOG_PARSE_RESULTS = True
  # Use smaller images in tests
  MAX_IMAGE_WIDTH = 1000
  MAX_IMAGE_HEIGHT = 1000


def get_config(env: str = None) -> object:
  """
  Get configuration based on environment.

  Args:
    env: Environment name ('development', 'production', 'testing')
         If None, uses OCR_ENV environment variable or defaults to 'development'

  Returns:
    Configuration class
  """
  if env is None:
    env = os.getenv("OCR_ENV", "development")

  config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
  }

  return config_map.get(env.lower(), DevelopmentConfig)


# Export commonly used configs
__all__ = [
  "OCRConfig",
  "ParserConfig",
  "ServiceConfig",
  "DevelopmentConfig",
  "ProductionConfig",
  "TestingConfig",
  "get_config",
]
