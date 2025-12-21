"""add source_id to recipe

Revision ID: add_source_id
Revises: add_image_fields
Create Date: 2025-12-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_source_id'
down_revision: Union[str, None] = 'add_image_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add source_id column to recipe table"""
    op.add_column('recipe', sa.Column('source_id', sa.String(), nullable=True))
    op.create_index('ix_recipe_source_id', 'recipe', ['source_id'], unique=False)


def downgrade() -> None:
    """Remove source_id column from recipe table"""
    op.drop_index('ix_recipe_source_id', table_name='recipe')
    op.drop_column('recipe', 'source_id')
