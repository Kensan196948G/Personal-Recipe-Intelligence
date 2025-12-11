"""
Example Usage of OCR Module

This script demonstrates various ways to use the OCR module
for extracting recipe data from images.
"""

import logging
from pathlib import Path

from backend.ocr import OCRExtractor, OCRService, RecipeParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def example_basic_usage():
    """Example: Basic OCR processing."""
    print("\n=== Example 1: Basic Usage ===")

    # Initialize service
    service = OCRService(lang="jpn+eng")

    # Process an image
    image_path = "/path/to/recipe_image.jpg"

    result = service.process_image(
        image_path=image_path,
        preprocess=True,
        include_confidence=True,
    )

    if result["status"] == "ok":
        data = result["data"]
        print(f"\nTitle: {data['title']}")
        print(f"\nIngredients ({len(data['ingredients'])}):")
        for i, ingredient in enumerate(data["ingredients"], 1):
            print(f"  {i}. {ingredient}")

        print(f"\nSteps ({len(data['steps'])}):")
        for i, step in enumerate(data["steps"], 1):
            print(f"  {i}. {step}")

        if "confidence" in result:
            print(f"\nOCR Confidence: {result['confidence']}%")
    else:
        print(f"Error: {result['error']}")


def example_validation():
    """Example: Validate image before processing."""
    print("\n=== Example 2: Image Validation ===")

    service = OCRService()
    image_path = "/path/to/recipe_image.jpg"

    # Validate first
    validation = service.validate_image(image_path)

    if validation["valid"]:
        info = validation["info"]
        print("\nImage is valid:")
        print(f"  Size: {info['width']}x{info['height']}")
        print(f"  Format: {info['format']}")
        print(f"  File size: {info['size_kb']:.2f} KB")

        # Proceed with processing
        _result = service.process_image(image_path)
        # ... process result (using _result)
    else:
        print(f"Invalid image: {validation['error']}")


def example_text_only():
    """Example: Extract text only without parsing."""
    print("\n=== Example 3: Text-Only Extraction ===")

    service = OCRService()
    image_path = "/path/to/recipe_image.jpg"

    result = service.extract_text_only(
        image_path=image_path,
        preprocess=True,
    )

    if result["status"] == "ok":
        print("\nExtracted Text:")
        print("-" * 50)
        print(result["text"])
        print("-" * 50)
    else:
        print(f"Error: {result['error']}")


def example_batch_processing():
    """Example: Batch process multiple images."""
    print("\n=== Example 4: Batch Processing ===")

    service = OCRService()

    # List of image paths
    image_paths = [
        "/path/to/recipe1.jpg",
        "/path/to/recipe2.jpg",
        "/path/to/recipe3.jpg",
    ]

    result = service.batch_process(
        image_paths=image_paths,
        preprocess=True,
    )

    print("\nBatch Processing Summary:")
    print(f"  Total: {result['summary']['total']}")
    print(f"  Success: {result['summary']['success']}")
    print(f"  Errors: {result['summary']['error']}")

    # Process results
    for item in result["results"]:
        source = Path(item["source"]).name
        if item["status"] == "ok":
            title = item["data"]["title"]
            print(f"\n✓ {source}: {title}")
        else:
            print(f"\n✗ {source}: {item['error']}")


def example_ingredient_normalization():
    """Example: Normalize ingredient strings."""
    print("\n=== Example 5: Ingredient Normalization ===")

    service = OCRService()

    # Raw ingredient strings from OCR
    ingredients = [
        "牛肉 500g",
        "玉ねぎ 2個",
        "カレールー 1箱",
        "水 200ml",
        "砂糖 大さじ2",
        "塩 少々",
    ]

    normalized = service.normalize_ingredients(ingredients)

    print("\nNormalized Ingredients:")
    for item in normalized:
        name = item["name"]
        qty = item["quantity"]
        unit = item["unit"]

        if qty is not None:
            print(f"  {name}: {qty} {unit or ''}")
        else:
            print(f"  {name}: (no quantity)")


def example_low_level_usage():
    """Example: Using low-level components directly."""
    print("\n=== Example 6: Low-Level Usage ===")

    # Use OCRExtractor directly
    extractor = OCRExtractor(lang="jpn+eng")
    image_path = "/path/to/recipe_image.jpg"

    # Extract text with confidence
    text, confidence = extractor.extract_with_confidence(
        image_path=image_path,
        preprocess=True,
    )

    print(f"\nExtracted text (confidence: {confidence:.2f}%):")
    print(text[:200] + "...")

    # Use RecipeParser directly
    parser = RecipeParser()
    recipe_data = parser.parse(text)

    print("\nParsed Recipe:")
    print(f"  Title: {recipe_data['title']}")
    print(f"  Ingredients: {len(recipe_data['ingredients'])}")
    print(f"  Steps: {len(recipe_data['steps'])}")


def example_custom_configuration():
    """Example: Custom configuration for specific needs."""
    print("\n=== Example 7: Custom Configuration ===")

    # Japanese only, larger image size
    service = OCRService(
        lang="jpn",  # Japanese only
        max_width=3000,  # Allow larger images
        max_height=3000,
    )

    # Process with custom settings
    result = service.process_image(
        image_path="/path/to/japanese_recipe.jpg",
        preprocess=True,  # Enable preprocessing
        include_confidence=True,
    )

    if result["status"] == "ok":
        print("Processed with custom settings:")
        print(f"  Confidence: {result.get('confidence', 'N/A')}%")
        print(f"  Title: {result['data']['title']}")


def example_error_handling():
    """Example: Proper error handling."""
    print("\n=== Example 8: Error Handling ===")

    service = OCRService()

    # Try processing various scenarios
    test_cases = [
        "/path/to/valid_image.jpg",
        "/path/to/nonexistent.jpg",
        "/path/to/corrupted.jpg",
    ]

    for image_path in test_cases:
        print(f"\nProcessing: {image_path}")

        try:
            result = service.process_image(image_path)

            if result["status"] == "ok":
                print("  ✓ Success")
                print(f"    Title: {result['data']['title']}")
            else:
                print("  ✗ Failed")
                print(f"    Error: {result['error']}")

        except Exception as e:
            print(f"  ✗ Exception: {e}")


def main():
    """Run all examples."""
    print("OCR Module - Example Usage")
    print("=" * 60)

    # Note: These examples won't run without actual image files
    # Uncomment individual examples as needed

    # example_basic_usage()
    # example_validation()
    # example_text_only()
    # example_batch_processing()
    # example_ingredient_normalization()
    # example_low_level_usage()
    # example_custom_configuration()
    # example_error_handling()

    print("\nNote: Update image paths and uncomment examples to test")


if __name__ == "__main__":
    main()
