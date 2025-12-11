"""Database models for Personal Recipe Intelligence.

This module defines SQLAlchemy ORM models for recipes, ingredients, and tags.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    ForeignKey,
    Table,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# Association tables for many-to-many relationships
recipe_tag_association = Table(
    "recipe_tag",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipe.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)


class Recipe(Base):
    """Recipe model representing a single recipe."""

    __tablename__ = "recipe"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_url = Column(String(512), nullable=True)
    source_type = Column(String(50), nullable=False)  # 'web', 'ocr', 'manual'
    servings = Column(Integer, nullable=True)
    prep_time_minutes = Column(Integer, nullable=True)
    cook_time_minutes = Column(Integer, nullable=True)
    total_time_minutes = Column(Integer, nullable=True)
    difficulty = Column(String(20), nullable=True)  # 'easy', 'medium', 'hard'
    image_url = Column(String(512), nullable=True)
    image_path = Column(String(512), nullable=True)
    notes = Column(Text, nullable=True)
    is_favorite = Column(Boolean, default=False)
    rating = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    ingredients = relationship(
        "Ingredient", back_populates="recipe", cascade="all, delete-orphan"
    )
    steps = relationship("Step", back_populates="recipe", cascade="all, delete-orphan")
    tags = relationship(
        "Tag", secondary=recipe_tag_association, back_populates="recipes"
    )

    def __repr__(self) -> str:
        """String representation of Recipe."""
        return f"<Recipe(id={self.id}, title='{self.title}', source_type='{self.source_type}')>"


class Ingredient(Base):
    """Ingredient model for recipe ingredients."""

    __tablename__ = "ingredient"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipe.id"), nullable=False)
    name = Column(String(255), nullable=False)
    name_normalized = Column(String(255), nullable=False)  # For normalized search
    quantity = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    original_text = Column(String(512), nullable=True)
    order_index = Column(Integer, nullable=False, default=0)

    # Relationships
    recipe = relationship("Recipe", back_populates="ingredients")

    def __repr__(self) -> str:
        """String representation of Ingredient."""
        return f"<Ingredient(id={self.id}, name='{self.name}', quantity={self.quantity}, unit='{self.unit}')>"


class Step(Base):
    """Step model for recipe cooking steps."""

    __tablename__ = "step"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipe.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    instruction = Column(Text, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    image_url = Column(String(512), nullable=True)

    # Relationships
    recipe = relationship("Recipe", back_populates="steps")

    def __repr__(self) -> str:
        """String representation of Step."""
        return f"<Step(id={self.id}, step_number={self.step_number}, recipe_id={self.recipe_id})>"


class Tag(Base):
    """Tag model for categorizing recipes."""

    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(
        String(50), nullable=True
    )  # 'cuisine', 'meal_type', 'dietary', etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    recipes = relationship(
        "Recipe", secondary=recipe_tag_association, back_populates="tags"
    )

    def __repr__(self) -> str:
        """String representation of Tag."""
        return f"<Tag(id={self.id}, name='{self.name}', category='{self.category}')>"
