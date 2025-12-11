#!/bin/bash
# Create model and additional schema files for N+1 optimization

set -e

echo "Creating model and additional files..."

# Create models directory
mkdir -p backend/models

# Create recipe models
cat > backend/models/recipe.py << 'EOF'
"""Recipe database models with optimized relationships."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.database import Base


class Recipe(Base):
  """Recipe model with eager loading configuration."""

  __tablename__ = "recipes"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String(500), nullable=False, index=True)
  description = Column(Text, nullable=True)
  source_url = Column(String(1000), nullable=True)
  image_url = Column(String(1000), nullable=True)
  prep_time = Column(Integer, nullable=True)
  cook_time = Column(Integer, nullable=True)
  servings = Column(Integer, nullable=True)
  created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
  updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

  # Relationships with cascade delete
  ingredients = relationship(
    "Ingredient",
    back_populates="recipe",
    cascade="all, delete-orphan",
    lazy="select",
  )
  steps = relationship(
    "Step",
    back_populates="recipe",
    cascade="all, delete-orphan",
    order_by="Step.step_number",
    lazy="select",
  )
  tags = relationship(
    "RecipeTag",
    back_populates="recipe",
    cascade="all, delete-orphan",
    lazy="select",
  )

  def __repr__(self):
    return f"<Recipe(id={self.id}, name='{self.name}')>"


class Ingredient(Base):
  """Ingredient model with normalized name."""

  __tablename__ = "ingredients"

  id = Column(Integer, primary_key=True, index=True)
  recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
  name = Column(String(200), nullable=False)
  quantity = Column(String(50), nullable=False)
  unit = Column(String(50), nullable=True)
  normalized_name = Column(String(200), nullable=False, index=True)

  recipe = relationship("Recipe", back_populates="ingredients")

  def __repr__(self):
    return f"<Ingredient(id={self.id}, name='{self.name}')>"


class Step(Base):
  """Recipe step model with ordering."""

  __tablename__ = "steps"

  id = Column(Integer, primary_key=True, index=True)
  recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
  step_number = Column(Integer, nullable=False)
  description = Column(Text, nullable=False)

  recipe = relationship("Recipe", back_populates="steps")

  def __repr__(self):
    return f"<Step(id={self.id}, step_number={self.step_number})>"


class RecipeTag(Base):
  """Recipe tag model for categorization."""

  __tablename__ = "recipe_tags"

  id = Column(Integer, primary_key=True, index=True)
  recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
  name = Column(String(100), nullable=False, index=True)

  recipe = relationship("Recipe", back_populates="tags")

  def __repr__(self):
    return f"<RecipeTag(id={self.id}, name='{self.name}')>"
EOF

echo "Created backend/models/recipe.py"

# Create API dependencies file
mkdir -p backend/api
cat > backend/api/dependencies.py << 'EOF'
"""API dependencies for dependency injection."""

from sqlalchemy.orm import Session
from backend.database import SessionLocal


def get_db():
  """Get database session.

  Yields:
      Database session

  Usage:
      @router.get("/")
      async def endpoint(db: Session = Depends(get_db)):
          ...
  """
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
EOF

echo "Created backend/api/dependencies.py"

# Create database configuration file
cat > backend/database.py << 'EOF'
"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/recipes.db")

# Create engine
engine = create_engine(
  DATABASE_URL,
  connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
  echo=False,  # Set to True for query logging in development
  pool_pre_ping=True,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def init_db():
  """Initialize database tables.

  Creates all tables defined in models.
  """
  Base.metadata.create_all(bind=engine)


def get_db_session():
  """Get a database session context manager.

  Usage:
      with get_db_session() as db:
          # Use db session
  """
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
EOF

echo "Created backend/database.py"

# Create performance monitoring utility
mkdir -p backend/utils
cat > backend/utils/performance.py << 'EOF'
"""Performance monitoring utilities."""

import time
import logging
from functools import wraps
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class QueryLogger:
  """Log SQL queries for performance analysis."""

  def __init__(self):
    self.queries = []
    self.enabled = False

  def enable(self):
    """Enable query logging."""
    self.enabled = True
    event.listen(Engine, "before_cursor_execute", self._before_cursor_execute)
    event.listen(Engine, "after_cursor_execute", self._after_cursor_execute)

  def disable(self):
    """Disable query logging."""
    self.enabled = False
    event.remove(Engine, "before_cursor_execute", self._before_cursor_execute)
    event.remove(Engine, "after_cursor_execute", self._after_cursor_execute)

  def _before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

  def _after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - context._query_start_time
    self.queries.append({
      "statement": statement,
      "parameters": parameters,
      "duration": total_time,
    })
    if total_time > 0.1:  # Log slow queries (>100ms)
      logger.warning(f"Slow query ({total_time:.3f}s): {statement[:100]}...")

  def get_stats(self):
    """Get query statistics."""
    if not self.queries:
      return {
        "total_queries": 0,
        "total_time": 0,
        "avg_time": 0,
        "slowest": None,
      }

    total_time = sum(q["duration"] for q in self.queries)
    slowest = max(self.queries, key=lambda q: q["duration"])

    return {
      "total_queries": len(self.queries),
      "total_time": total_time,
      "avg_time": total_time / len(self.queries),
      "slowest": {
        "duration": slowest["duration"],
        "statement": slowest["statement"][:200],
      },
    }

  def reset(self):
    """Reset query log."""
    self.queries = []


def timer(func):
  """Decorator to measure function execution time."""
  @wraps(func)
  async def async_wrapper(*args, **kwargs):
    start = time.time()
    result = await func(*args, **kwargs)
    duration = time.time() - start
    logger.info(f"{func.__name__} took {duration:.3f}s")
    return result

  @wraps(func)
  def sync_wrapper(*args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    duration = time.time() - start
    logger.info(f"{func.__name__} took {duration:.3f}s")
    return result

  if hasattr(func, "__call__") and hasattr(func, "__await__"):
    return async_wrapper
  return sync_wrapper
EOF

echo "Created backend/utils/performance.py"

echo ""
echo "Model and utility files created successfully!"
echo ""
echo "Files created:"
echo "  - backend/models/recipe.py"
echo "  - backend/api/dependencies.py"
echo "  - backend/database.py"
echo "  - backend/utils/performance.py"

chmod +x "$0"
