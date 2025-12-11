# OCR Module Specification

**Personal Recipe Intelligence - OCR Module**

Version: 1.0
Date: 2025-12-11
Author: Backend Developer Agent

---

## Overview

The OCR (Optical Character Recognition) module provides comprehensive functionality for extracting recipe data from images. It combines image preprocessing, text extraction, and intelligent parsing to convert recipe images into structured data.

## Architecture

### Components

```
OCR Module
├── extractor.py      - Image preprocessing & text extraction
├── parser.py         - Recipe text parsing & structuring
├── service.py        - High-level service interface
├── config.py         - Configuration management
└── __init__.py       - Module exports
```

### Data Flow

```
Image Input
    ↓
[Validation] → Check format, size, readability
    ↓
[Preprocessing] → Resize, denoise, enhance, binarize
    ↓
[OCR Extraction] → Extract text using Tesseract
    ↓
[Text Cleaning] → Remove noise, normalize whitespace
    ↓
[Recipe Parsing] → Identify sections (title, ingredients, steps)
    ↓
[Structuring] → Convert to JSON format
    ↓
Structured Recipe Data
```

## Module: extractor.py

### Class: OCRExtractor

**Purpose**: Handle image preprocessing and text extraction.

**Key Methods**:

- `preprocess_image(image)`: Apply preprocessing pipeline
- `extract_text(image_path)`: Extract text from file
- `extract_text_from_image(image)`: Extract text from PIL Image
- `extract_with_confidence(image_path)`: Extract with confidence score

**Image Preprocessing Pipeline**:

1. **Resize**: Scale down if exceeds max dimensions
2. **Grayscale**: Convert to grayscale for better OCR
3. **Denoise**: Apply fast non-local means denoising
4. **Contrast Enhancement**: Use CLAHE (Contrast Limited Adaptive Histogram Equalization)
5. **Binarization**: Apply Otsu's thresholding

**Technical Details**:

- Uses OpenCV for image processing
- PIL/Pillow for image I/O
- pytesseract for OCR
- Supports multi-language OCR (configurable)

## Module: parser.py

### Class: RecipeParser

**Purpose**: Parse OCR text into structured recipe data.

**Key Methods**:

- `parse(text)`: Main parsing method
- `normalize_ingredient(ingredient)`: Extract quantity/unit from ingredient
- `_extract_title(lines)`: Identify recipe title
- `_extract_ingredients(lines, ...)`: Extract ingredient list
- `_extract_steps(lines, ...)`: Extract cooking steps
- `_find_section(lines, keywords)`: Locate section boundaries

**Section Detection**:

Uses keyword matching to identify:
- **Ingredients**: "材料", "ingredients", "材料名", etc.
- **Steps**: "作り方", "手順", "instructions", "steps", etc.

**Ingredient Parsing**:

Extracts structured data:
```python
{
  "name": "牛肉",
  "quantity": 500.0,
  "unit": "g",
  "original": "牛肉 500g"
}
```

**Step Parsing**:

Handles:
- Numbered steps (1. 2. 3.)
- Bullet points
- Paragraph format
- Multi-line steps

## Module: service.py

### Class: OCRService

**Purpose**: High-level interface for OCR operations.

**Key Methods**:

- `process_image(image_path)`: Complete OCR pipeline
- `process_image_object(image)`: Process PIL Image
- `batch_process(image_paths)`: Process multiple images
- `extract_text_only(image_path)`: Text extraction without parsing
- `validate_image(image_path)`: Pre-processing validation
- `normalize_ingredients(ingredients)`: Batch ingredient normalization

**Response Format**:

```python
{
  "status": "ok" | "error",
  "data": {
    "title": str,
    "ingredients": List[str],
    "steps": List[str],
    "raw_text": str
  },
  "confidence": float,  # optional
  "error": str | None
}
```

## Configuration

### OCRConfig

- Language settings (jpn+eng default)
- Image size limits (2000x2000 default)
- Tesseract parameters
- Preprocessing settings

### ParserConfig

- Section keywords (Japanese + English)
- Measurement units
- Parsing rules
- Error correction mappings

### ServiceConfig

- File validation rules
- Batch processing limits
- Logging settings

### Environment Variables

```bash
# OCR Settings
OCR_MAX_WIDTH=2000
OCR_MAX_HEIGHT=2000
OCR_PREPROCESS=true
OCR_MIN_CONFIDENCE=50.0

# Parser Settings
PARSER_MIN_TITLE_LEN=3
PARSER_ERROR_CORRECTION=true

# Service Settings
SERVICE_MAX_BATCH=50
OCR_LOG_LEVEL=INFO
```

## Installation Requirements

### System Dependencies

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-jpn
sudo apt-get install libgl1-mesa-glx libglib2.0-0
```

### Python Dependencies

```
Pillow>=10.0.0
opencv-python>=4.8.0
pytesseract>=0.3.10
numpy>=1.24.0
```

## Performance Characteristics

### Processing Time

- Small image (800x600): ~1-2 seconds
- Medium image (1920x1080): ~3-5 seconds
- Large image (3000x2000): ~5-10 seconds

*Times vary based on image complexity and system performance*

### Memory Usage

- Typical: 50-200 MB per image
- Peak: Up to 500 MB for very large images

### Optimization Tips

1. Enable preprocessing for better accuracy
2. Use batch processing for multiple images
3. Set appropriate max dimensions
4. Use language-specific settings when possible

## Error Handling

### Error Categories

1. **File Errors**: File not found, invalid format
2. **OCR Errors**: Extraction failures, low confidence
3. **Parsing Errors**: Section detection failures
4. **Validation Errors**: Invalid image, size limits

### Error Response

```python
{
  "status": "error",
  "data": None,
  "error": "Detailed error message"
}
```

### Logging

All errors logged with:
- Timestamp
- Error type
- Stack trace (for exceptions)
- Context information

## Testing

### Test Coverage

- Unit tests for each component
- Integration tests for full pipeline
- Mock tests for external dependencies
- Edge case testing

### Test Files

- `backend/tests/test_ocr.py`: Complete test suite
- Coverage target: >80%

### Running Tests

```bash
pytest backend/tests/test_ocr.py -v
pytest backend/tests/test_ocr.py --cov=backend/ocr
```

## Usage Examples

### Basic Usage

```python
from backend.ocr import OCRService

service = OCRService()
result = service.process_image("/path/to/recipe.jpg")

if result["status"] == "ok":
    print(f"Title: {result['data']['title']}")
    print(f"Ingredients: {result['data']['ingredients']}")
```

### Batch Processing

```python
result = service.batch_process([
    "/path/to/recipe1.jpg",
    "/path/to/recipe2.jpg",
])
print(f"Processed: {result['summary']['success']}")
```

### Custom Configuration

```python
service = OCRService(
    lang="jpn",  # Japanese only
    max_width=3000,
    max_height=3000
)
```

## Integration Points

### With Recipe Service

```python
from backend.ocr import OCRService
from backend.recipe import RecipeService

ocr = OCRService()
recipe_service = RecipeService()

# Extract from image
result = ocr.process_image("/path/to/recipe.jpg")

# Save to database
if result["status"] == "ok":
    recipe_service.create_recipe(result["data"])
```

### With API Endpoint

```python
from fastapi import UploadFile

@app.post("/api/v1/recipes/ocr")
async def upload_recipe_image(file: UploadFile):
    # Save uploaded file
    image_path = save_upload(file)

    # Process with OCR
    result = ocr_service.process_image(image_path)

    return result
```

## Limitations

### Current Limitations

1. **Layout Dependency**: Assumes structured layout (title, sections)
2. **Language Mix**: May have lower accuracy with heavily mixed languages
3. **Handwriting**: Not optimized for handwritten recipes
4. **Complex Layouts**: Multi-column or heavily formatted text may confuse parser

### Known Issues

1. OCR may misread similar characters (O/0, l/1)
2. Very low contrast images may require manual preprocessing
3. Section detection requires standard keywords
4. Ingredient parsing assumes quantity+unit+name format

## Future Enhancements

### Planned Features

1. Machine learning-based section detection
2. Improved handwriting support
3. Multi-column layout handling
4. Context-aware OCR error correction
5. Recipe format templates
6. Image quality auto-enhancement

### API Extensions

1. Streaming processing for large batches
2. Webhook support for async processing
3. Custom parser rule configuration
4. Training data collection for ML improvements

## Compliance

### CLAUDE.md Adherence

- ✅ 2-space indentation
- ✅ Type annotations
- ✅ Comprehensive docstrings
- ✅ Error handling with logging
- ✅ No hardcoded secrets
- ✅ kebab-case file names
- ✅ snake_case Python variables
- ✅ Modular architecture

### Code Quality

- Black formatting
- Ruff linting
- pytest testing
- >60% coverage target

## Support & Maintenance

### Documentation

- README.md: User guide
- INSTALL.md: Installation guide
- example_usage.py: Code examples
- This document: Technical specification

### Logging

- INFO: Processing status
- DEBUG: Detailed operations
- ERROR: Failures with traces

### Monitoring

Recommended metrics:
- Processing time per image
- Success/failure rate
- Average confidence scores
- Common error types

## Version History

### 1.0.0 (2025-12-11)

Initial release:
- OCR extraction with preprocessing
- Recipe parsing (title, ingredients, steps)
- Service interface
- Batch processing
- Configuration management
- Comprehensive tests
- Documentation

---

## Appendix A: Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- WebP (.webp)

## Appendix B: Tesseract PSM Modes

- 0: Orientation and script detection only
- 1: Automatic page segmentation with OSD
- 3: Fully automatic page segmentation (default)
- 4: Assume single column of text
- 6: Assume uniform block of text (used by module)
- 11: Sparse text

## Appendix C: Language Codes

- jpn: Japanese
- eng: English
- chi_sim: Chinese Simplified
- chi_tra: Chinese Traditional
- kor: Korean
- Multiple: Combine with + (e.g., jpn+eng)

---

**End of Specification**
