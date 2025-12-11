# OCR Module - Personal Recipe Intelligence

OCR (Optical Character Recognition) module for extracting recipe data from images.

## Features

- **Image Preprocessing**: Resize, denoise, enhance contrast, binarization
- **Text Extraction**: Multi-language OCR support (Japanese + English)
- **Recipe Parsing**: Automatic detection of title, ingredients, and cooking steps
- **Batch Processing**: Process multiple images efficiently
- **Error Handling**: Comprehensive logging and error recovery

## Installation

### System Requirements

Install Tesseract OCR on Ubuntu:

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-jpn
```

### Python Dependencies

```bash
pip install -r backend/ocr/requirements.txt
```

## Usage

### Basic OCR Processing

```python
from backend.ocr import OCRService

# Initialize service
ocr_service = OCRService(lang="jpn+eng")

# Process an image
result = ocr_service.process_image(
  image_path="/path/to/recipe_image.jpg",
  preprocess=True,
  include_confidence=True
)

if result["status"] == "ok":
  recipe_data = result["data"]
  print(f"Title: {recipe_data['title']}")
  print(f"Ingredients: {recipe_data['ingredients']}")
  print(f"Steps: {recipe_data['steps']}")
  print(f"Confidence: {result['confidence']}%")
```

### Extract Text Only

```python
# Extract raw text without parsing
result = ocr_service.extract_text_only(
  image_path="/path/to/image.jpg",
  preprocess=True
)

if result["status"] == "ok":
  print(result["text"])
```

### Batch Processing

```python
# Process multiple images
image_paths = [
  "/path/to/recipe1.jpg",
  "/path/to/recipe2.jpg",
  "/path/to/recipe3.jpg"
]

result = ocr_service.batch_process(
  image_paths=image_paths,
  preprocess=True
)

print(f"Success: {result['summary']['success']}")
print(f"Errors: {result['summary']['error']}")

for item in result["results"]:
  if item["status"] == "ok":
    print(f"Processed: {item['source']}")
```

### Normalize Ingredients

```python
# Normalize ingredient strings
ingredients = [
  "牛肉 500g",
  "玉ねぎ 2個",
  "カレールー 1箱"
]

normalized = ocr_service.normalize_ingredients(ingredients)

for item in normalized:
  print(f"Name: {item['name']}, Qty: {item['quantity']}, Unit: {item['unit']}")
```

### Validate Image

```python
# Check if image is valid before processing
result = ocr_service.validate_image("/path/to/image.jpg")

if result["valid"]:
  info = result["info"]
  print(f"Size: {info['width']}x{info['height']}")
  print(f"Format: {info['format']}")
else:
  print(f"Invalid: {result['error']}")
```

## Components

### OCRExtractor

Low-level text extraction with image preprocessing.

```python
from backend.ocr import OCRExtractor

extractor = OCRExtractor(lang="jpn+eng")

# Extract text with confidence score
text, confidence = extractor.extract_with_confidence(
  image_path="/path/to/image.jpg",
  preprocess=True
)
```

### RecipeParser

Parse OCR text into structured recipe data.

```python
from backend.ocr import RecipeParser

parser = RecipeParser()

# Parse raw OCR text
recipe_data = parser.parse(text)
```

## Configuration

### Language Support

Set language in OCRExtractor or OCRService initialization:

```python
# Japanese only
ocr_service = OCRService(lang="jpn")

# English only
ocr_service = OCRService(lang="eng")

# Japanese + English (default)
ocr_service = OCRService(lang="jpn+eng")

# Multiple languages
ocr_service = OCRService(lang="jpn+eng+chi_sim")
```

### Image Size Limits

Configure maximum image dimensions:

```python
ocr_service = OCRService(
  max_width=3000,
  max_height=3000
)
```

## Response Format

All service methods return a consistent format:

```python
{
  "status": "ok",  # or "error"
  "data": {
    "title": "Recipe Title",
    "ingredients": ["ingredient 1", "ingredient 2"],
    "steps": ["step 1", "step 2"],
    "raw_text": "original OCR text..."
  },
  "confidence": 87.5,  # optional
  "error": null  # or error message
}
```

## Error Handling

The module includes comprehensive error handling:

- Invalid image files
- OCR extraction failures
- Parsing errors
- File not found errors

All errors are logged and returned in the response:

```python
result = ocr_service.process_image("/invalid/path.jpg")

if result["status"] == "error":
  print(f"Error: {result['error']}")
```

## Logging

Configure logging in your application:

```python
import logging

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

Log levels:
- INFO: Processing status and results
- DEBUG: Detailed processing information
- ERROR: Errors and exceptions with stack traces

## Performance Tips

1. **Enable preprocessing**: Usually improves accuracy significantly
2. **Batch processing**: More efficient for multiple images
3. **Image size**: Resize very large images before processing
4. **Image quality**: Higher quality images = better results

## Troubleshooting

### Low Confidence Scores

- Enable preprocessing
- Check image quality (contrast, blur)
- Verify correct language setting
- Try different image formats

### Missing Sections

- Check if section keywords are detected
- Verify text layout is structured
- Review raw_text in response

### Installation Issues

Verify Tesseract installation:

```bash
tesseract --version
tesseract --list-langs
```

Should show "jpn" in the language list for Japanese support.
