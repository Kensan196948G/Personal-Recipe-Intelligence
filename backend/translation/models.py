"""
Translation models for Personal Recipe Intelligence.

This module defines data models for translation requests and results.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Language(str, Enum):
    """Supported languages for translation."""

    EN_US = "EN-US"
    EN_GB = "EN-GB"
    JA = "JA"
    ZH = "ZH"
    KO = "KO"
    DE = "DE"
    FR = "FR"
    ES = "ES"
    IT = "IT"
    PT = "PT-PT"
    PT_BR = "PT-BR"
    RU = "RU"


class TranslationRequest(BaseModel):
    """Request model for translation."""

    text: str = Field(..., description="Text to translate")
    target_lang: Language = Field(..., description="Target language code")
    source_lang: Optional[Language] = Field(
        None, description="Source language code (auto-detect if None)"
    )

    class Config:
        use_enum_values = True


class TranslationResult(BaseModel):
    """Result model for translation."""

    original_text: str = Field(..., description="Original text")
    translated_text: str = Field(..., description="Translated text")
    source_lang: str = Field(..., description="Detected or specified source language")
    target_lang: str = Field(..., description="Target language")
    cached: bool = Field(default=False, description="Whether result was from cache")


class RecipeTranslationRequest(BaseModel):
    """Request model for translating entire recipe."""

    recipe_id: str = Field(..., description="Recipe ID to translate")
    target_lang: Language = Field(..., description="Target language code")

    class Config:
        use_enum_values = True


class RecipeTranslationResult(BaseModel):
    """Result model for translated recipe."""

    recipe_id: str = Field(..., description="Recipe ID")
    target_lang: str = Field(..., description="Target language")
    title: Optional[str] = Field(None, description="Translated title")
    description: Optional[str] = Field(None, description="Translated description")
    ingredients: List[str] = Field(
        default_factory=list, description="Translated ingredients"
    )
    steps: List[str] = Field(
        default_factory=list, description="Translated cooking steps"
    )
    cached_count: int = Field(
        default=0, description="Number of cached translations used"
    )
