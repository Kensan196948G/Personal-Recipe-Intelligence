"""
OCR Text Extractor Module

This module handles image preprocessing and text extraction using pytesseract.
Supports Japanese language OCR with error handling and image enhancement.
"""

import logging
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


class OCRExtractor:
    """
    OCR text extractor with image preprocessing capabilities.

    Supports:
    - Image preprocessing (resize, enhance contrast, denoise)
    - Multi-language text extraction (Japanese + English)
    - Error handling and logging
    """

    def __init__(
        self,
        lang: str = "jpn+eng",
        max_width: int = 2000,
        max_height: int = 2000,
    ):
        """
        Initialize OCR extractor.

        Args:
          lang: Tesseract language codes (e.g., 'jpn+eng')
          max_width: Maximum image width for processing
          max_height: Maximum image height for processing
        """
        self.lang = lang
        self.max_width = max_width
        self.max_height = max_height
        logger.info(f"OCRExtractor initialized with lang={lang}")

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.

        Steps:
        1. Resize if too large
        2. Convert to grayscale
        3. Enhance contrast
        4. Denoise
        5. Binarization (Otsu's method)

        Args:
          image: PIL Image object

        Returns:
          Preprocessed PIL Image
        """
        try:
            # Resize if necessary
            image = self._resize_image(image)

            # Convert PIL to OpenCV format
            img_array = np.array(image)

            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array

            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

            # Enhance contrast using CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)

            # Binarization using Otsu's method
            _, binary = cv2.threshold(
                enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

            # Convert back to PIL Image
            processed_image = Image.fromarray(binary)

            logger.debug("Image preprocessing completed successfully")
            return processed_image

        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}", exc_info=True)
            # Return original image if preprocessing fails
            return image

    def _resize_image(self, image: Image.Image) -> Image.Image:
        """
        Resize image if it exceeds maximum dimensions.

        Args:
          image: PIL Image object

        Returns:
          Resized PIL Image
        """
        width, height = image.size

        if width <= self.max_width and height <= self.max_height:
            return image

        # Calculate scaling factor
        scale = min(self.max_width / width, self.max_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)

        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.debug(f"Image resized from {width}x{height} to {new_width}x{new_height}")

        return resized

    def extract_text(
        self,
        image_path: str | Path,
        preprocess: bool = True,
    ) -> str:
        """
        Extract text from image file using OCR.

        Args:
          image_path: Path to image file
          preprocess: Whether to preprocess the image

        Returns:
          Extracted text as string

        Raises:
          FileNotFoundError: If image file not found
          ValueError: If image cannot be processed
        """
        try:
            image_path = Path(image_path)

            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            # Load image
            image = Image.open(image_path)
            logger.info(f"Processing image: {image_path.name}")

            return self.extract_text_from_image(image, preprocess=preprocess)

        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"Failed to extract text from {image_path}: {e}", exc_info=True
            )
            raise ValueError(f"Image processing error: {e}") from e

    def extract_text_from_image(
        self,
        image: Image.Image,
        preprocess: bool = True,
    ) -> str:
        """
        Extract text from PIL Image object using OCR.

        Args:
          image: PIL Image object
          preprocess: Whether to preprocess the image

        Returns:
          Extracted text as string

        Raises:
          ValueError: If OCR extraction fails
        """
        try:
            # Preprocess if requested
            if preprocess:
                processed_image = self.preprocess_image(image)
            else:
                processed_image = image

            # Extract text using pytesseract
            text = pytesseract.image_to_string(
                processed_image,
                lang=self.lang,
                config="--psm 6",  # Assume uniform block of text
            )

            # Clean up extracted text
            cleaned_text = self._clean_text(text)

            logger.info(f"Extracted {len(cleaned_text)} characters from image")
            logger.debug(f"Extracted text preview: {cleaned_text[:100]}...")

            return cleaned_text

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}", exc_info=True)
            raise ValueError(f"OCR extraction error: {e}") from e

    def _clean_text(self, text: str) -> str:
        """
        Clean up extracted text.

        - Remove excessive whitespace
        - Normalize line breaks
        - Remove empty lines

        Args:
          text: Raw OCR text

        Returns:
          Cleaned text
        """
        if not text:
            return ""

        # Split into lines
        lines = text.split("\n")

        # Remove empty lines and strip whitespace
        cleaned_lines = [line.strip() for line in lines if line.strip()]

        # Join with single line break
        cleaned_text = "\n".join(cleaned_lines)

        return cleaned_text

    def extract_with_confidence(
        self,
        image_path: str | Path,
        preprocess: bool = True,
    ) -> Tuple[str, float]:
        """
        Extract text with confidence score.

        Args:
          image_path: Path to image file
          preprocess: Whether to preprocess the image

        Returns:
          Tuple of (extracted_text, average_confidence)

        Raises:
          FileNotFoundError: If image file not found
          ValueError: If image cannot be processed
        """
        try:
            image_path = Path(image_path)

            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            # Load image
            image = Image.open(image_path)

            # Preprocess if requested
            if preprocess:
                processed_image = self.preprocess_image(image)
            else:
                processed_image = image

            # Extract text with detailed data
            data = pytesseract.image_to_data(
                processed_image,
                lang=self.lang,
                config="--psm 6",
                output_type=pytesseract.Output.DICT,
            )

            # Calculate average confidence (excluding -1 values)
            confidences = [float(conf) for conf in data["conf"] if int(conf) != -1]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # Extract text
            text = pytesseract.image_to_string(
                processed_image,
                lang=self.lang,
                config="--psm 6",
            )

            cleaned_text = self._clean_text(text)

            logger.info(
                f"Extracted text from {image_path.name} with confidence: {avg_confidence:.2f}%"
            )

            return cleaned_text, avg_confidence

        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"Failed to extract text with confidence from {image_path}: {e}",
                exc_info=True,
            )
            raise ValueError(f"OCR extraction error: {e}") from e
