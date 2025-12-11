"""
OCR Service Module

This module provides a high-level OCR service for processing uploaded images
and converting them into structured recipe data.
"""

import logging
from pathlib import Path
from typing import Dict

from PIL import Image

from .extractor import OCRExtractor
from .parser import RecipeParser

logger = logging.getLogger(__name__)


class OCRService:
    """
    High-level OCR service for recipe image processing.

    Combines OCR extraction and recipe parsing to provide
    structured recipe data from images.
    """

    def __init__(
        self,
        lang: str = "jpn+eng",
        max_width: int = 2000,
        max_height: int = 2000,
    ):
        """
        Initialize OCR service.

        Args:
          lang: Tesseract language codes
          max_width: Maximum image width for processing
          max_height: Maximum image height for processing
        """
        self.extractor = OCRExtractor(
            lang=lang,
            max_width=max_width,
            max_height=max_height,
        )
        self.parser = RecipeParser()
        logger.info("OCRService initialized")

    def process_image(
        self,
        image_path: str | Path,
        preprocess: bool = True,
        include_confidence: bool = False,
    ) -> Dict[str, any]:
        """
        Process image file and extract structured recipe data.

        Args:
          image_path: Path to image file
          preprocess: Whether to preprocess image
          include_confidence: Whether to include OCR confidence score

        Returns:
          Dictionary containing:
            - status: "ok" or "error"
            - data: Structured recipe data (title, ingredients, steps)
            - confidence: OCR confidence score (if requested)
            - error: Error message (if failed)

        Example:
          {
            "status": "ok",
            "data": {
              "title": "Chicken Curry",
              "ingredients": ["Chicken 500g", "Onion 2"],
              "steps": ["Cut chicken", "Cook curry"],
              "raw_text": "..."
            },
            "confidence": 87.5,
            "error": null
          }
        """
        try:
            logger.info(f"Processing image: {image_path}")

            # Extract text from image
            if include_confidence:
                text, confidence = self.extractor.extract_with_confidence(
                    image_path=image_path,
                    preprocess=preprocess,
                )
            else:
                text = self.extractor.extract_text(
                    image_path=image_path,
                    preprocess=preprocess,
                )
                confidence = None

            # Parse recipe from text
            recipe_data = self.parser.parse(text)

            # Build response
            response = {
                "status": "ok",
                "data": recipe_data,
                "error": None,
            }

            if include_confidence and confidence is not None:
                response["confidence"] = round(confidence, 2)

            logger.info(
                f"Successfully processed image: {Path(image_path).name}, "
                f"extracted {len(recipe_data['ingredients'])} ingredients, "
                f"{len(recipe_data['steps'])} steps"
            )

            return response

        except FileNotFoundError as e:
            logger.error(f"Image file not found: {image_path}")
            return {
                "status": "error",
                "data": None,
                "error": f"Image file not found: {e}",
            }

        except Exception as e:
            logger.error(f"Failed to process image {image_path}: {e}", exc_info=True)
            return {
                "status": "error",
                "data": None,
                "error": f"Processing failed: {str(e)}",
            }

    def process_image_object(
        self,
        image: Image.Image,
        preprocess: bool = True,
    ) -> Dict[str, any]:
        """
        Process PIL Image object and extract structured recipe data.

        Args:
          image: PIL Image object
          preprocess: Whether to preprocess image

        Returns:
          Dictionary containing status, data, and error fields
        """
        try:
            logger.info("Processing PIL Image object")

            # Extract text from image
            text = self.extractor.extract_text_from_image(
                image=image,
                preprocess=preprocess,
            )

            # Parse recipe from text
            recipe_data = self.parser.parse(text)

            response = {
                "status": "ok",
                "data": recipe_data,
                "error": None,
            }

            logger.info(
                f"Successfully processed image object, "
                f"extracted {len(recipe_data['ingredients'])} ingredients, "
                f"{len(recipe_data['steps'])} steps"
            )

            return response

        except Exception as e:
            logger.error(f"Failed to process image object: {e}", exc_info=True)
            return {
                "status": "error",
                "data": None,
                "error": f"Processing failed: {str(e)}",
            }

    def batch_process(
        self,
        image_paths: list[str | Path],
        preprocess: bool = True,
    ) -> Dict[str, any]:
        """
        Process multiple images in batch.

        Args:
          image_paths: List of image file paths
          preprocess: Whether to preprocess images

        Returns:
          Dictionary containing:
            - status: "ok" or "partial" or "error"
            - results: List of processing results for each image
            - summary: Success/failure counts
            - error: Error message (if completely failed)
        """
        try:
            logger.info(f"Batch processing {len(image_paths)} images")

            results = []
            success_count = 0
            error_count = 0

            for image_path in image_paths:
                result = self.process_image(
                    image_path=image_path,
                    preprocess=preprocess,
                    include_confidence=True,
                )

                # Add source path to result
                result["source"] = str(image_path)

                if result["status"] == "ok":
                    success_count += 1
                else:
                    error_count += 1

                results.append(result)

            # Determine overall status
            if error_count == 0:
                status = "ok"
            elif success_count == 0:
                status = "error"
            else:
                status = "partial"

            response = {
                "status": status,
                "results": results,
                "summary": {
                    "total": len(image_paths),
                    "success": success_count,
                    "error": error_count,
                },
                "error": None,
            }

            logger.info(
                f"Batch processing completed: "
                f"{success_count} succeeded, {error_count} failed"
            )

            return response

        except Exception as e:
            logger.error(f"Batch processing failed: {e}", exc_info=True)
            return {
                "status": "error",
                "results": [],
                "summary": {
                    "total": len(image_paths),
                    "success": 0,
                    "error": len(image_paths),
                },
                "error": f"Batch processing failed: {str(e)}",
            }

    def normalize_ingredients(self, ingredients: list[str]) -> list[Dict[str, any]]:
        """
        Normalize list of ingredient strings into structured data.

        Args:
          ingredients: List of raw ingredient strings

        Returns:
          List of normalized ingredient dictionaries
        """
        try:
            normalized = []

            for ingredient in ingredients:
                normalized_ingredient = self.parser.normalize_ingredient(ingredient)
                normalized.append(normalized_ingredient)

            logger.debug(f"Normalized {len(normalized)} ingredients")
            return normalized

        except Exception as e:
            logger.error(f"Failed to normalize ingredients: {e}", exc_info=True)
            return []

    def extract_text_only(
        self,
        image_path: str | Path,
        preprocess: bool = True,
    ) -> Dict[str, any]:
        """
        Extract only text from image without parsing.

        Useful for debugging or when raw text is needed.

        Args:
          image_path: Path to image file
          preprocess: Whether to preprocess image

        Returns:
          Dictionary containing status, text, and error fields
        """
        try:
            logger.info(f"Extracting text only from: {image_path}")

            text = self.extractor.extract_text(
                image_path=image_path,
                preprocess=preprocess,
            )

            return {
                "status": "ok",
                "text": text,
                "error": None,
            }

        except Exception as e:
            logger.error(
                f"Failed to extract text from {image_path}: {e}", exc_info=True
            )
            return {
                "status": "error",
                "text": None,
                "error": f"Extraction failed: {str(e)}",
            }

    def validate_image(self, image_path: str | Path) -> Dict[str, any]:
        """
        Validate image file before processing.

        Checks:
        - File exists
        - File is a valid image
        - Image can be loaded

        Args:
          image_path: Path to image file

        Returns:
          Dictionary containing:
            - valid: Boolean indicating if image is valid
            - error: Error message if invalid
            - info: Image information (width, height, format)
        """
        try:
            image_path = Path(image_path)

            # Check if file exists
            if not image_path.exists():
                return {
                    "valid": False,
                    "error": "File not found",
                    "info": None,
                }

            # Try to load image
            image = Image.open(image_path)

            # Get image info
            info = {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "size_kb": image_path.stat().st_size / 1024,
            }

            image.close()

            logger.debug(f"Image validated: {image_path.name}, info: {info}")

            return {
                "valid": True,
                "error": None,
                "info": info,
            }

        except Exception as e:
            logger.error(
                f"Image validation failed for {image_path}: {e}", exc_info=True
            )
            return {
                "valid": False,
                "error": f"Invalid image: {str(e)}",
                "info": None,
            }
