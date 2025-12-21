"""Add performance indexes for search and sort optimization

Revision ID: 001
Revises:
Create Date: 2025-12-11

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add indexes for performance optimization."""
    # Recipe table indexes
    op.create_index("ix_recipe_title", "recipe", ["title"], unique=False)
    op.create_index("ix_recipe_created_at", "recipe", ["created_at"], unique=False)

    # Ingredient table indexes
    op.create_index("ix_ingredient_name", "ingredient", ["name"], unique=False)
    op.create_index(
        "ix_ingredient_name_normalized", "ingredient", ["name_normalized"], unique=False
    )

    # Tag table unique index
    op.create_index("ix_tag_name", "tag", ["name"], unique=True)

    # Composite indexes for common queries
    op.create_index(
        "ix_recipe_created_at_title", "recipe", ["created_at", "title"], unique=False
    )


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index("ix_recipe_created_at_title", table_name="recipe")
    op.drop_index("ix_tag_name", table_name="tag")
    op.drop_index("ix_ingredient_name_normalized", table_name="ingredient")
    op.drop_index("ix_ingredient_name", table_name="ingredient")
    op.drop_index("ix_recipe_created_at", table_name="recipe")
    op.drop_index("ix_recipe_title", table_name="recipe")
