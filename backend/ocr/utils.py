"""
OCR Utility Functions

Helper functions for image processing, validation, and text manipulation.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image

logger = logging.getLogger(__name__)


def is_valid_image_file(file_path: str | Path) -> bool:
  """
  Check if file is a valid image.

  Args:
    file_path: Path to file

  Returns:
    True if valid image file
  """
  valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

  try:
    file_path = Path(file_path)

    # Check extension
    if file_path.suffix.lower() not in valid_extensions:
      return False

    # Check if file exists
    if not file_path.exists():
      return False

    # Try to open with PIL
    with Image.open(file_path) as img:
      img.verify()

    return True

  except Exception as e:
    logger.debug(f"Invalid image file {file_path}: {e}")
    return False


def get_image_dimensions(file_path: str | Path) -> Optional[Tuple[int, int]]:
  """
  Get image dimensions without loading full image.

  Args:
    file_path: Path to image file

  Returns:
    Tuple of (width, height) or None if failed
  """
  try:
    with Image.open(file_path) as img:
      return img.size
  except Exception as e:
    logger.error(f"Failed to get dimensions for {file_path}: {e}")
    return None


def get_image_info(file_path: str | Path) -> Optional[Dict[str, any]]:
  """
  Get comprehensive image information.

  Args:
    file_path: Path to image file

  Returns:
    Dictionary with image info or None
  """
  try:
    file_path = Path(file_path)

    with Image.open(file_path) as img:
      info = {
        "path": str(file_path),
        "filename": file_path.name,
        "width": img.width,
        "height": img.height,
        "format": img.format,
        "mode": img.mode,
        "size_bytes": file_path.stat().st_size,
        "size_kb": round(file_path.stat().st_size / 1024, 2),
        "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
      }

    return info

  except Exception as e:
    logger.error(f"Failed to get info for {file_path}: {e}")
    return None


def find_image_files(directory: str | Path, recursive: bool = False) -> List[Path]:
  """
  Find all image files in directory.

  Args:
    directory: Directory to search
    recursive: Whether to search subdirectories

  Returns:
    List of image file paths
  """
  valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

  directory = Path(directory)
  image_files = []

  if not directory.exists():
    logger.error(f"Directory not found: {directory}")
    return []

  try:
    if recursive:
      for ext in valid_extensions:
        image_files.extend(directory.rglob(f"*{ext}"))
    else:
      for ext in valid_extensions:
        image_files.extend(directory.glob(f"*{ext}"))

    logger.info(f"Found {len(image_files)} image files in {directory}")
    return sorted(image_files)

  except Exception as e:
    logger.error(f"Failed to search directory {directory}: {e}")
    return []


def clean_text(text: str) -> str:
  """
  Clean and normalize text.

  Args:
    text: Raw text

  Returns:
    Cleaned text
  """
  if not text:
    return ""

  # Remove excessive whitespace
  text = re.sub(r"\s+", " ", text)

  # Remove leading/trailing whitespace
  text = text.strip()

  return text


def split_into_lines(text: str, remove_empty: bool = True) -> List[str]:
  """
  Split text into lines.

  Args:
    text: Text to split
    remove_empty: Whether to remove empty lines

  Returns:
    List of lines
  """
  lines = text.split("\n")

  if remove_empty:
    lines = [line.strip() for line in lines if line.strip()]
  else:
    lines = [line.strip() for line in lines]

  return lines


def extract_numbers(text: str) -> List[float]:
  """
  Extract all numbers from text.

  Args:
    text: Text to search

  Returns:
    List of numbers found
  """
  # Pattern for integers and decimals
  pattern = r"\d+(?:\.\d+)?"
  matches = re.findall(pattern, text)
  return [float(m) for m in matches]


def has_japanese(text: str) -> bool:
  """
  Check if text contains Japanese characters.

  Args:
    text: Text to check

  Returns:
    True if contains Japanese
  """
  # Japanese character ranges
  japanese_pattern = r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]"
  return bool(re.search(japanese_pattern, text))


def has_english(text: str) -> bool:
  """
  Check if text contains English characters.

  Args:
    text: Text to check

  Returns:
    True if contains English
  """
  return bool(re.search(r"[a-zA-Z]", text))


def detect_language(text: str) -> str:
  """
  Simple language detection.

  Args:
    text: Text to analyze

  Returns:
    Language code: 'jpn', 'eng', 'mixed', or 'unknown'
  """
  has_jp = has_japanese(text)
  has_en = has_english(text)

  if has_jp and has_en:
    return "mixed"
  elif has_jp:
    return "jpn"
  elif has_en:
    return "eng"
  else:
    return "unknown"


def extract_quantities(text: str) -> List[Dict[str, any]]:
  """
  Extract quantities with units from text.

  Args:
    text: Text to parse

  Returns:
    List of dictionaries with quantity info
  """
  # Common units
  units = r"(g|kg|ml|l|cc|カップ|個|本|枚|切れ|片|大さじ|小さじ|適量|少々|cup|tbsp|tsp|oz|lb)"

  # Pattern: number + optional unit
  pattern = rf"(\d+(?:\.\d+)?)\s*({units})?"

  matches = re.findall(pattern, text, re.IGNORECASE)

  quantities = []
  for match in matches:
    quantity = {
      "value": float(match[0]),
      "unit": match[1] if match[1] else None,
    }
    quantities.append(quantity)

  return quantities


def normalize_whitespace(text: str) -> str:
  """
  Normalize whitespace in text.

  Args:
    text: Text to normalize

  Returns:
    Normalized text
  """
  # Replace multiple spaces with single space
  text = re.sub(r" +", " ", text)

  # Replace multiple newlines with single newline
  text = re.sub(r"\n+", "\n", text)

  # Remove spaces before punctuation
  text = re.sub(r"\s+([,.:;!?])", r"\1", text)

  return text.strip()


def is_likely_title(text: str, min_length: int = 3, max_length: int = 100) -> bool:
  """
  Check if text is likely a recipe title.

  Args:
    text: Text to check
    min_length: Minimum length
    max_length: Maximum length

  Returns:
    True if likely a title
  """
  if not text or len(text) < min_length or len(text) > max_length:
    return False

  # Should not be just numbers
  if re.match(r"^[\d\s\-\.\,]+$", text):
    return False

  # Should not contain typical section keywords
  section_keywords = [
    "材料",
    "作り方",
    "ingredients",
    "instructions",
    "directions",
    "steps",
  ]
  text_lower = text.lower()
  if any(keyword in text_lower for keyword in section_keywords):
    return False

  return True


def format_ingredient_list(ingredients: List[str]) -> str:
  """
  Format ingredient list for display.

  Args:
    ingredients: List of ingredients

  Returns:
    Formatted string
  """
  if not ingredients:
    return "No ingredients found"

  formatted = []
  for i, ingredient in enumerate(ingredients, 1):
    formatted.append(f"{i}. {ingredient}")

  return "\n".join(formatted)


def format_step_list(steps: List[str]) -> str:
  """
  Format cooking steps for display.

  Args:
    steps: List of steps

  Returns:
    Formatted string
  """
  if not steps:
    return "No steps found"

  formatted = []
  for i, step in enumerate(steps, 1):
    formatted.append(f"{i}. {step}")

  return "\n".join(formatted)


def calculate_text_similarity(text1: str, text2: str) -> float:
  """
  Calculate simple text similarity (Jaccard similarity).

  Args:
    text1: First text
    text2: Second text

  Returns:
    Similarity score (0.0 to 1.0)
  """
  # Convert to sets of words
  words1 = set(text1.lower().split())
  words2 = set(text2.lower().split())

  if not words1 and not words2:
    return 1.0

  if not words1 or not words2:
    return 0.0

  # Calculate Jaccard similarity
  intersection = len(words1 & words2)
  union = len(words1 | words2)

  return intersection / union if union > 0 else 0.0


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
  """
  Truncate text to maximum length.

  Args:
    text: Text to truncate
    max_length: Maximum length
    suffix: Suffix to add if truncated

  Returns:
    Truncated text
  """
  if not text or len(text) <= max_length:
    return text

  return text[: max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
  """
  Sanitize filename by removing invalid characters.

  Args:
    filename: Original filename

  Returns:
    Sanitized filename
  """
  # Remove invalid characters
  filename = re.sub(r'[<>:"/\\|?*]', "", filename)

  # Replace spaces with underscores
  filename = filename.replace(" ", "_")

  # Limit length
  if len(filename) > 255:
    name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
    filename = name[:250] + ("." + ext if ext else "")

  return filename


# Export all utility functions
__all__ = [
  "is_valid_image_file",
  "get_image_dimensions",
  "get_image_info",
  "find_image_files",
  "clean_text",
  "split_into_lines",
  "extract_numbers",
  "has_japanese",
  "has_english",
  "detect_language",
  "extract_quantities",
  "normalize_whitespace",
  "is_likely_title",
  "format_ingredient_list",
  "format_step_list",
  "calculate_text_similarity",
  "truncate_text",
  "sanitize_filename",
]
