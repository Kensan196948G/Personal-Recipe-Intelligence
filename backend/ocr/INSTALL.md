# OCR Module Installation Guide

Complete installation guide for the OCR module on Ubuntu (headless/CLI).

## Prerequisites

- Ubuntu Linux (tested on 20.04+)
- Python 3.11
- SSH access (if remote)
- sudo privileges

## Step 1: Install System Dependencies

### Install Tesseract OCR

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

### Install Japanese Language Pack

For Japanese recipe support:

```bash
sudo apt-get install -y tesseract-ocr-jpn
```

### Install Additional Language Packs (Optional)

```bash
# English (usually included)
sudo apt-get install -y tesseract-ocr-eng

# Chinese Simplified
sudo apt-get install -y tesseract-ocr-chi-sim

# Korean
sudo apt-get install -y tesseract-ocr-kor
```

### Install Image Processing Libraries

```bash
sudo apt-get install -y \
  libgl1-mesa-glx \
  libglib2.0-0 \
  libsm6 \
  libxext6 \
  libxrender-dev
```

## Step 2: Verify Tesseract Installation

Check Tesseract version:

```bash
tesseract --version
```

Expected output:
```
tesseract 4.x.x
 leptonica-1.x.x
  ...
```

List available languages:

```bash
tesseract --list-langs
```

Expected output should include:
```
List of available languages (x):
eng
jpn
...
```

## Step 3: Install Python Dependencies

Navigate to project directory:

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
```

Install OCR module dependencies:

```bash
pip install -r backend/ocr/requirements.txt
```

Or install individually:

```bash
pip install Pillow>=10.0.0
pip install opencv-python>=4.8.0
pip install pytesseract>=0.3.10
pip install numpy>=1.24.0
```

## Step 4: Verify Python Installation

Create a test script:

```bash
cat > /tmp/test_ocr.py << 'EOF'
import pytesseract
import cv2
from PIL import Image
import numpy as np

print("Checking imports...")
print(f"pytesseract version: {pytesseract.__version__}")
print(f"OpenCV version: {cv2.__version__}")
print(f"PIL version: {Image.__version__}")
print(f"NumPy version: {np.__version__}")

print("\nChecking Tesseract...")
print(f"Tesseract path: {pytesseract.get_tesseract_version()}")

print("\nAll checks passed!")
EOF

python /tmp/test_ocr.py
```

## Step 5: Test OCR Module

Create a simple test:

```bash
python << 'EOF'
from backend.ocr import OCRService

service = OCRService(lang="jpn+eng")
print("OCR Service initialized successfully!")
print(f"Extractor: {service.extractor}")
print(f"Parser: {service.parser}")
EOF
```

## Step 6: Test with Sample Image (Optional)

Create a test image with text:

```bash
# Create a simple test image with Python
python << 'EOF'
from PIL import Image, ImageDraw, ImageFont

# Create white image
img = Image.new('RGB', (800, 600), color='white')
draw = ImageDraw.Draw(img)

# Add text (using default font)
text = """Recipe Title
材料
Chicken 500g
玉ねぎ 2個
作り方
1. Cut chicken
2. Cook curry"""

draw.text((50, 50), text, fill='black')
img.save('/tmp/test_recipe.png')
print("Test image created: /tmp/test_recipe.png")
EOF
```

Test OCR on the image:

```bash
python << 'EOF'
from backend.ocr import OCRService

service = OCRService()
result = service.process_image('/tmp/test_recipe.png')

if result['status'] == 'ok':
    print("OCR Test Successful!")
    print(f"Title: {result['data']['title']}")
    print(f"Ingredients: {len(result['data']['ingredients'])}")
    print(f"Steps: {len(result['data']['steps'])}")
else:
    print(f"OCR Test Failed: {result['error']}")
EOF
```

## Troubleshooting

### Issue: "tesseract is not installed"

**Solution:**
```bash
# Verify tesseract is in PATH
which tesseract

# If not found, install again
sudo apt-get install --reinstall tesseract-ocr
```

### Issue: "Language 'jpn' not found"

**Solution:**
```bash
# Install Japanese language pack
sudo apt-get install tesseract-ocr-jpn

# Verify installation
tesseract --list-langs | grep jpn
```

### Issue: "ImportError: libGL.so.1"

**Solution:**
```bash
# Install missing OpenCV dependencies
sudo apt-get install -y libgl1-mesa-glx
```

### Issue: "ImportError: libgthread-2.0.so.0"

**Solution:**
```bash
# Install missing glib libraries
sudo apt-get install -y libglib2.0-0
```

### Issue: Low OCR accuracy

**Solutions:**
1. Enable preprocessing:
   ```python
   result = service.process_image(image_path, preprocess=True)
   ```

2. Check image quality:
   ```python
   validation = service.validate_image(image_path)
   print(validation['info'])
   ```

3. Try different language settings:
   ```python
   service = OCRService(lang="jpn")  # Japanese only
   ```

### Issue: "Permission denied" on image files

**Solution:**
```bash
# Fix file permissions
chmod 644 /path/to/image.jpg

# Or if directory permission issue
chmod 755 /path/to/image/directory
```

## Performance Optimization

### For Large Images

Adjust max size in service initialization:

```python
service = OCRService(max_width=3000, max_height=3000)
```

### For Batch Processing

Use the batch processing method:

```python
result = service.batch_process(image_paths)
```

### Enable Logging

For debugging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Uninstallation

To remove OCR components:

```bash
# Remove Python packages
pip uninstall -y pytesseract opencv-python Pillow numpy

# Remove system packages
sudo apt-get remove --purge tesseract-ocr tesseract-ocr-jpn
sudo apt-get autoremove
```

## Next Steps

1. Read the [README.md](/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/ocr/README.md) for usage examples
2. Check [example_usage.py](/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/ocr/example_usage.py) for code samples
3. Run tests: `pytest backend/tests/test_ocr.py`
4. Integrate with your recipe service

## Support

For issues specific to:
- **Tesseract**: See [Tesseract documentation](https://tesseract-ocr.github.io/)
- **OpenCV**: See [OpenCV documentation](https://docs.opencv.org/)
- **This module**: Check logs and error messages
