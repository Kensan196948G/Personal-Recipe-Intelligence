# Translation Module

Translation service for Personal Recipe Intelligence using DeepL API.

## Features

- Translate recipe titles, descriptions, ingredients, and cooking steps
- Support for multiple languages (EN, JA, ZH, KO, DE, FR, ES, IT, PT, RU, etc.)
- In-memory caching with TTL to reduce API calls
- Batch translation for efficiency
- Complete recipe translation
- API usage monitoring
- Error handling for API failures

## Installation

Install the required dependency:

```bash
pip install deepl
```

## Configuration

Set your DeepL API key in the environment or settings:

```python
# In settings or .env
DEEPL_API_KEY=your_api_key_here
```

## Usage

### Initialize Service

```python
from backend.translation.service import TranslationService
from backend.translation.models import Language

# Initialize with API key
service = TranslationService(api_key="your_api_key", cache_ttl_minutes=60)
```

### Translate Single Text

```python
from backend.translation.models import Language

result = service.translate(
  text="Hello, World!",
  target_lang=Language.JA,
  source_lang=Language.EN_US,  # Optional, auto-detect if None
  use_cache=True
)

print(result.translated_text)  # こんにちは、世界！
print(result.cached)  # False (first call)
```

### Translate Multiple Texts (Batch)

```python
texts = ["Apple", "Banana", "Orange"]
results = service.translate_batch(
  texts=texts,
  target_lang=Language.JA,
  use_cache=True
)

for result in results:
  print(f"{result.original_text} -> {result.translated_text}")
```

### Translate Entire Recipe

```python
recipe_data = {
  "id": "recipe_001",
  "title": "Chicken Curry",
  "description": "A delicious curry recipe",
  "ingredients": [
    "500g chicken breast",
    "2 onions",
    "3 cloves garlic"
  ],
  "steps": [
    "Cut the chicken into cubes",
    "Chop the onions and garlic",
    "Cook everything together"
  ]
}

result = service.translate_recipe(
  recipe_data=recipe_data,
  target_lang=Language.JA,
  use_cache=True
)

print(result.title)  # チキンカレー
print(result.description)  # 美味しいカレーのレシピ
print(result.ingredients)  # ['500gの鶏胸肉', '玉ねぎ2個', 'にんにく3片']
print(result.steps)  # ['鶏肉を角切りにする', '玉ねぎとにんにくを刻む', 'すべてを一緒に調理する']
print(f"Used cache for {result.cached_count} translations")
```

### Check Cache Statistics

```python
stats = service.get_cache_stats()
print(f"Cache size: {stats['size']}")
```

### Clear Cache

```python
service.clear_cache()
```

### Check API Usage

```python
usage = service.check_usage()
print(f"Characters used: {usage['character_count']}/{usage['character_limit']}")
print(f"Usage: {usage['character_usage_percent']:.2f}%")
```

## Supported Languages

The following languages are supported via the `Language` enum:

- EN_US, EN_GB (English)
- JA (Japanese)
- ZH (Chinese)
- KO (Korean)
- DE (German)
- FR (French)
- ES (Spanish)
- IT (Italian)
- PT (Portuguese)
- PT_BR (Brazilian Portuguese)
- RU (Russian)

## Models

### TranslationRequest

```python
class TranslationRequest(BaseModel):
  text: str
  target_lang: Language
  source_lang: Optional[Language] = None
```

### TranslationResult

```python
class TranslationResult(BaseModel):
  original_text: str
  translated_text: str
  source_lang: str
  target_lang: str
  cached: bool
```

### RecipeTranslationRequest

```python
class RecipeTranslationRequest(BaseModel):
  recipe_id: str
  target_lang: Language
```

### RecipeTranslationResult

```python
class RecipeTranslationResult(BaseModel):
  recipe_id: str
  target_lang: str
  title: Optional[str]
  description: Optional[str]
  ingredients: List[str]
  steps: List[str]
  cached_count: int
```

## Caching

The translation service uses an in-memory cache to reduce API calls:

- Cache entries have a configurable TTL (default: 60 minutes)
- Cache keys are generated from text + target language + source language
- Cache is automatically cleared for expired entries
- Manual cache clearing is supported

## Error Handling

The service handles the following error cases:

- Empty or invalid API key (raises ValueError)
- DeepL API errors (raises Exception with message)
- Network errors (raises Exception)
- Empty text (returns as-is without API call)

All errors are logged using the Python logging module.

## Logging

The service logs the following events:

- Service initialization
- Translation requests (with text preview)
- Cache hits
- Batch translations
- API errors
- Cache operations

Configure logging level in your application:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.translation.service")
```

## Testing

Run tests with pytest:

```bash
pytest tests/test_translation_service.py -v
```

## Performance Considerations

- Use batch translation for multiple texts to reduce API calls
- Enable caching to avoid redundant translations
- Monitor API usage to stay within limits
- Consider adjusting cache TTL based on your needs

## Security

- API keys are never logged
- Credentials should be stored in environment variables or secure settings
- All API communication uses HTTPS (handled by DeepL library)

## Files

- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/translation/models.py` - Data models
- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/translation/service.py` - Translation service
- `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/tests/test_translation_service.py` - Unit tests
