"""Recipe schema definitions for API validation and serialization."""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class IngredientBase(BaseModel):
  """Base schema for ingredient data."""

  name: str = Field(..., min_length=1, max_length=200, description="Ingredient name")
  quantity: str = Field(..., max_length=50, description="Quantity (e.g., '1', '200g')")
  unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement")


class IngredientCreate(IngredientBase):
  """Schema for creating an ingredient."""

  pass


class IngredientResponse(IngredientBase):
  """Schema for ingredient in API responses."""

  id: int
  normalized_name: str = Field(..., description="Normalized ingredient name")

  class Config:
    orm_mode = True


class RecipeBase(BaseModel):
  """Base schema for recipe data."""

  name: str = Field(..., min_length=1, max_length=500, description="Recipe name")
  description: Optional[str] = Field(None, max_length=2000, description="Recipe description")
  source_url: Optional[str] = Field(None, max_length=1000, description="Source URL")
  image_url: Optional[str] = Field(None, max_length=1000, description="Image URL")
  prep_time: Optional[int] = Field(None, ge=0, description="Prep time in minutes")
  cook_time: Optional[int] = Field(None, ge=0, description="Cook time in minutes")
  servings: Optional[int] = Field(None, ge=1, description="Number of servings")


class RecipeCreate(RecipeBase):
  """Schema for creating a recipe."""

  ingredients: List[IngredientCreate] = Field(default_factory=list, description="List of ingredients")
  steps: List[str] = Field(default_factory=list, description="Cooking steps")
  tags: List[str] = Field(default_factory=list, description="Recipe tags")

  @validator("tags")
  def normalize_tags(cls, tags):
    """Normalize tags to lowercase."""
    return [tag.lower().strip() for tag in tags if tag.strip()]

  @validator("steps")
  def validate_steps(cls, steps):
    """Validate that steps are non-empty."""
    return [step.strip() for step in steps if step.strip()]


class RecipeUpdate(BaseModel):
  """Schema for updating a recipe."""

  name: Optional[str] = Field(None, min_length=1, max_length=500)
  description: Optional[str] = Field(None, max_length=2000)
  source_url: Optional[str] = Field(None, max_length=1000)
  image_url: Optional[str] = Field(None, max_length=1000)
  prep_time: Optional[int] = Field(None, ge=0)
  cook_time: Optional[int] = Field(None, ge=0)
  servings: Optional[int] = Field(None, ge=1)
  ingredients: Optional[List[IngredientCreate]] = None
  steps: Optional[List[str]] = None
  tags: Optional[List[str]] = None

  @validator("tags")
  def normalize_tags(cls, tags):
    """Normalize tags to lowercase."""
    if tags is None:
      return None
    return [tag.lower().strip() for tag in tags if tag.strip()]

  @validator("steps")
  def validate_steps(cls, steps):
    """Validate that steps are non-empty."""
    if steps is None:
      return None
    return [step.strip() for step in steps if step.strip()]


class StepResponse(BaseModel):
  """Schema for recipe step in API responses."""

  id: int
  step_number: int = Field(..., description="Step sequence number")
  description: str = Field(..., description="Step description")

  class Config:
    orm_mode = True


class TagResponse(BaseModel):
  """Schema for recipe tag in API responses."""

  id: int
  name: str = Field(..., description="Tag name")

  class Config:
    orm_mode = True


class RecipeResponse(RecipeBase):
  """Schema for recipe in API responses with all relations."""

  id: int
  ingredients: List[IngredientResponse] = Field(default_factory=list)
  steps: List[StepResponse] = Field(default_factory=list)
  tags: List[TagResponse] = Field(default_factory=list)
  created_at: Optional[str] = Field(None, description="Creation timestamp")
  updated_at: Optional[str] = Field(None, description="Last update timestamp")

  @property
  def total_time(self) -> Optional[int]:
    """Calculate total time (prep + cook)."""
    if self.prep_time is not None and self.cook_time is not None:
      return self.prep_time + self.cook_time
    return None

  class Config:
    orm_mode = True


class RecipePaginatedResponse(BaseModel):
  """Schema for paginated recipe list responses."""

  items: List[RecipeResponse] = Field(..., description="List of recipes")
  total: int = Field(..., ge=0, description="Total number of recipes")
  skip: int = Field(..., ge=0, description="Number of skipped records")
  limit: int = Field(..., ge=1, description="Maximum records returned")

  @property
  def has_next(self) -> bool:
    """Check if there are more pages."""
    return self.skip + self.limit < self.total

  @property
  def has_previous(self) -> bool:
    """Check if there are previous pages."""
    return self.skip > 0

  @property
  def page_count(self) -> int:
    """Calculate total number of pages."""
    if self.limit == 0:
      return 0
    return (self.total + self.limit - 1) // self.limit

  @property
  def current_page(self) -> int:
    """Calculate current page number (1-indexed)."""
    if self.limit == 0:
      return 0
    return (self.skip // self.limit) + 1


class RecipeSearchResponse(BaseModel):
  """Schema for recipe search results."""

  query: str = Field(..., description="Search query used")
  results: List[RecipeResponse] = Field(..., description="Matching recipes")
  count: int = Field(..., ge=0, description="Number of results")

  class Config:
    orm_mode = True


class RecipeStatsResponse(BaseModel):
  """Schema for recipe statistics."""

  total_recipes: int = Field(..., ge=0)
  total_ingredients: int = Field(..., ge=0)
  unique_tags: int = Field(..., ge=0)
  avg_prep_time: Optional[float] = None
  avg_cook_time: Optional[float] = None
  most_common_tags: List[str] = Field(default_factory=list)

  class Config:
    orm_mode = True
