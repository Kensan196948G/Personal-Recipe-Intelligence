# OCR Module - Quick Start Guide

Get up and running with the OCR module in 5 minutes.

## 1. Install System Dependencies (Ubuntu)

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-jpn libgl1-mesa-glx
```

## 2. Install Python Dependencies

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
pip install Pillow opencv-python pytesseract numpy
```

## 3. Verify Installation

```bash
# Check Tesseract
tesseract --version
tesseract --list-langs | grep jpn

# Check Python imports
python -c "from backend.ocr import OCRService; print('OK')"
```

## 4. Basic Usage

Create a test script `test_ocr.py`:

```python
from backend.ocr import OCRService

# Initialize service
service = OCRService(lang="jpn+eng")

# Process an image
result = service.process_image(
    image_path="/path/to/recipe_image.jpg",
    preprocess=True,
    include_confidence=True
)

# Check result
if result["status"] == "ok":
    data = result["data"]
    print(f"Title: {data['title']}")
    print(f"\nIngredients:")
    for ing in data["ingredients"]:
        print(f"  - {ing}")
    print(f"\nSteps:")
    for i, step in enumerate(data["steps"], 1):
        print(f"  {i}. {step}")
    print(f"\nConfidence: {result.get('confidence', 'N/A')}%")
else:
    print(f"Error: {result['error']}")
```

Run it:

```bash
python test_ocr.py
```

## 5. Common Use Cases

### Extract Text Only

```python
result = service.extract_text_only("/path/to/image.jpg")
print(result["text"])
```

### Validate Before Processing

```python
validation = service.validate_image("/path/to/image.jpg")
if validation["valid"]:
    result = service.process_image("/path/to/image.jpg")
```

### Process Multiple Images

```python
images = ["/path/to/img1.jpg", "/path/to/img2.jpg"]
result = service.batch_process(images)
print(f"Success: {result['summary']['success']}")
```

### Normalize Ingredients

```python
ingredients = ["牛肉 500g", "玉ねぎ 2個"]
normalized = service.normalize_ingredients(ingredients)
for item in normalized:
    print(f"{item['name']}: {item['quantity']} {item['unit']}")
```

## 6. Configuration

### Environment Variables

Create `.env` file:

```bash
# OCR Configuration
OCR_MAX_WIDTH=2000
OCR_MAX_HEIGHT=2000
OCR_PREPROCESS=true
OCR_LOG_LEVEL=INFO
```

### Custom Settings

```python
# Japanese only, larger images
service = OCRService(
    lang="jpn",
    max_width=3000,
    max_height=3000
)
```

## 7. Troubleshooting

### Low Accuracy?

```python
# Enable preprocessing
result = service.process_image(image_path, preprocess=True)

# Check confidence score
result = service.process_image(image_path, include_confidence=True)
print(f"Confidence: {result['confidence']}")
```

### Image Too Large?

```python
# Increase limits
service = OCRService(max_width=4000, max_height=4000)
```

### Wrong Language Detected?

```python
# Use specific language
service = OCRService(lang="jpn")  # Japanese only
service = OCRService(lang="eng")  # English only
```

## 8. Integration Example

```python
from backend.ocr import OCRService
from pathlib import Path

def process_recipe_folder(folder_path):
    """Process all images in a folder."""
    service = OCRService()
    folder = Path(folder_path)

    for image_file in folder.glob("*.jpg"):
        print(f"Processing {image_file.name}...")
        result = service.process_image(str(image_file))

        if result["status"] == "ok":
            # Save or process the recipe data
            print(f"  ✓ Title: {result['data']['title']}")
        else:
            print(f"  ✗ Error: {result['error']}")

# Usage
process_recipe_folder("/path/to/recipe/images")
```

## 9. Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [example_usage.py](example_usage.py) for more examples
- See [INSTALL.md](INSTALL.md) for advanced installation
- Review [tests/test_ocr.py](../tests/test_ocr.py) for testing examples

## 10. Need Help?

1. Check logs:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Validate image:
   ```python
   validation = service.validate_image("/path/to/image.jpg")
   print(validation)
   ```

3. Test with simple image:
   ```bash
   # Create test image
   python << EOF
   from PIL import Image, ImageDraw
   img = Image.new('RGB', (800, 600), 'white')
   draw = ImageDraw.Draw(img)
   draw.text((50, 50), "Test Recipe\n材料\nChicken 500g", fill='black')
   img.save('/tmp/test.png')
   EOF

   # Process it
   python -c "from backend.ocr import OCRService; s=OCRService(); print(s.process_image('/tmp/test.png'))"
   ```

---

**You're all set! Start extracting recipes from images.**
