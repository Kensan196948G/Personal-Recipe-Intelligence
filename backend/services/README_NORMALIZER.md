# Ingredient Normalizer Service

## Overview

The Ingredient Normalizer Service provides comprehensive normalization of Japanese recipe ingredient data. It handles ingredient name standardization, quantity parsing (including fractions and Japanese cooking terms), and unit conversion.

## Features

- **Ingredient Name Normalization**: Converts various ingredient name formats to canonical forms
  - Handles kanji, hiragana, katakana, and English variations
  - Example: `玉ねぎ`, `玉葱`, `タマネギ` → `たまねぎ`

- **Quantity Parsing**: Parses numeric quantities including:
  - Simple numbers: `2`, `1.5`
  - Fractions: `1/2`, `2/3`
  - Mixed numbers: `1と1/2`, `1 1/2`
  - Ranges: `2-3`, `100〜200`
  - Japanese keywords: `少々`, `適量`, `ひとつまみ`

- **Unit Standardization**: Normalizes measurement units
  - Weight: `グラム` → `g`, `キログラム` → `kg`
  - Volume: `ミリリットル` → `ml`, `cc` → `ml`
  - Cooking: `大さじ`, `小さじ`, `カップ`
  - Count: `個`, `本`, `枚`, `切れ`

## Installation

No additional dependencies required beyond the standard library.

```bash
# The normalizer uses only standard Python libraries
python3 -m pip install pytest  # for running tests
```

## Configuration

The normalizer uses `/config/ingredient_mappings.json` for synonym mappings. This file contains:

- `ingredient_synonyms`: Maps ingredient variations to canonical names
- `unit_synonyms`: Maps unit variations to standard units
- `quantity_keywords`: Defines special quantity keywords (少々, 適量, etc.)

## Usage

### Basic Usage

```python
from services.normalizer import IngredientNormalizer

# Initialize normalizer
normalizer = IngredientNormalizer()

# Normalize a single ingredient
result = normalizer.normalize("玉ねぎ 1/2個")
print(f"Name: {result.name}")        # たまねぎ
print(f"Quantity: {result.quantity}") # 0.5
print(f"Unit: {result.unit}")        # 個
```

### Batch Normalization

```python
ingredients = [
  "玉ねぎ 1/2個",
  "醤油 大さじ2",
  "塩 少々",
  "豚肉 200g"
]

results = normalizer.normalize_batch(ingredients)

for result in results:
  print(f"{result.name}: {result.quantity} {result.unit}")
```

### Individual Component Normalization

```python
# Normalize ingredient name only
name = normalizer.normalize_ingredient_name("タマネギ")  # → たまねぎ

# Normalize unit only
unit = normalizer.normalize_unit("グラム")  # → g

# Parse quantity only
quantity, note = normalizer.parse_quantity("1/2")  # → (0.5, None)
quantity, note = normalizer.parse_quantity("少々")  # → (None, "少々")
```

### Convert to Dictionary

```python
result = normalizer.normalize("玉ねぎ 1/2個")
data = normalizer.to_dict(result)

# Returns:
# {
#   "name": "たまねぎ",
#   "quantity": "0.5",
#   "unit": "個",
#   "original_text": "玉ねぎ 1/2個",
#   "note": None
# }
```

## API Reference

### `IngredientNormalizer`

Main class for ingredient normalization.

#### Constructor

```python
IngredientNormalizer(mappings_path: Optional[str] = None)
```

- `mappings_path`: Path to ingredient_mappings.json (optional)

#### Methods

##### `normalize(ingredient_text: str) -> NormalizedIngredient`

Normalize a complete ingredient string.

**Parameters:**
- `ingredient_text`: Full ingredient text (e.g., "玉ねぎ 1/2個")

**Returns:**
- `NormalizedIngredient` object with parsed data

##### `normalize_ingredient_name(name: str) -> str`

Normalize only the ingredient name.

**Parameters:**
- `name`: Original ingredient name

**Returns:**
- Normalized ingredient name string

##### `normalize_unit(unit: str) -> str`

Normalize only the measurement unit.

**Parameters:**
- `unit`: Original unit string

**Returns:**
- Normalized unit string

##### `parse_quantity(quantity_str: str) -> Tuple[Optional[Decimal], Optional[str]]`

Parse quantity string into numeric value and note.

**Parameters:**
- `quantity_str`: Quantity string to parse

**Returns:**
- Tuple of (quantity as Decimal or None, note/keyword)

##### `normalize_batch(ingredients: list[str]) -> list[NormalizedIngredient]`

Normalize multiple ingredients at once.

**Parameters:**
- `ingredients`: List of ingredient text strings

**Returns:**
- List of NormalizedIngredient objects

##### `to_dict(normalized: NormalizedIngredient) -> Dict[str, Any]`

Convert NormalizedIngredient to dictionary.

**Parameters:**
- `normalized`: NormalizedIngredient object

**Returns:**
- Dictionary representation

### `NormalizedIngredient`

Data class representing normalized ingredient data.

**Attributes:**
- `name` (str): Normalized ingredient name
- `quantity` (Optional[Decimal]): Parsed quantity value
- `unit` (Optional[str]): Normalized unit
- `original_text` (str): Original input text
- `note` (Optional[str]): Additional notes (e.g., "少々", "range: 2-3")

## Examples

### Example 1: Parsing Various Formats

```python
test_ingredients = [
  "玉ねぎ 1/2個",           # Half an onion
  "醤油 大さじ2",           # 2 tablespoons soy sauce
  "塩 少々",               # A pinch of salt
  "豚バラ肉 200g",         # 200g pork belly
  "ニンジン 1本",          # 1 carrot
  "小麦粉 適量",           # Flour as needed
  "牛乳 200ml",           # 200ml milk
  "砂糖 大さじ1と1/2",     # 1.5 tablespoons sugar
]

normalizer = IngredientNormalizer()

for ingredient in test_ingredients:
  result = normalizer.normalize(ingredient)
  print(f"{result.name}: {result.quantity} {result.unit}")
```

### Example 2: Integration with Recipe Parser

```python
def parse_recipe_ingredients(raw_ingredients: list[str]) -> list[dict]:
  """Parse and normalize recipe ingredients."""
  normalizer = IngredientNormalizer()

  normalized_list = []
  for ingredient in raw_ingredients:
    result = normalizer.normalize(ingredient)
    normalized_list.append(normalizer.to_dict(result))

  return normalized_list

# Usage
raw_data = ["玉ねぎ 1個", "醤油 大さじ2", "塩 少々"]
parsed = parse_recipe_ingredients(raw_data)
```

### Example 3: Custom Mappings Path

```python
# Use custom mappings file
normalizer = IngredientNormalizer(
  mappings_path="/custom/path/to/mappings.json"
)
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest backend/tests/test_normalizer.py -v

# Run specific test class
pytest backend/tests/test_normalizer.py::TestQuantityParsing -v

# Run with coverage
pytest backend/tests/test_normalizer.py --cov=backend/services/normalizer
```

## Extending the Normalizer

### Adding New Ingredient Synonyms

Edit `/config/ingredient_mappings.json`:

```json
{
  "ingredient_synonyms": {
    "新しい材料": "正規化された名前",
    "別名": "正規化された名前"
  }
}
```

### Adding New Units

```json
{
  "unit_synonyms": {
    "新しい単位": "標準単位"
  }
}
```

### Adding New Quantity Keywords

```json
{
  "quantity_keywords": {
    "新しいキーワード": "標準化されたキーワード"
  }
}
```

## Performance Considerations

- The normalizer loads mappings once at initialization
- Normalization operations are O(1) for lookups
- Batch operations are more efficient than individual calls
- No external API calls or database queries required

## Thread Safety

The `IngredientNormalizer` is thread-safe for read operations after initialization. The mapping dictionaries are immutable after loading.

## Error Handling

- `FileNotFoundError`: Raised if mappings file is not found
- `ValueError`: Raised if mappings file contains invalid JSON
- Graceful degradation: Unknown ingredients/units are returned as-is

## Future Enhancements

Potential improvements:
- Machine learning-based ingredient recognition
- Support for more languages
- Automatic unit conversion (e.g., cups to ml)
- Nutrition data integration
- Allergen detection

## License

Part of Personal Recipe Intelligence project.

## Contact

For issues or questions, please refer to the main project documentation.
