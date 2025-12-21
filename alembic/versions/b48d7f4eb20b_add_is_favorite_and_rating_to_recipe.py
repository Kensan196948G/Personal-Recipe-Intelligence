"""add_is_favorite_and_rating_to_recipe

Revision ID: b48d7f4eb20b
Revises: add_shopping_list
Create Date: 2025-12-21 08:53:12.994637

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b48d7f4eb20b'
down_revision: Union[str, Sequence[str], None] = 'add_shopping_list'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('recipe', sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('recipe', sa.Column('rating', sa.Integer(), nullable=True))
    op.create_index('ix_recipe_is_favorite', 'recipe', ['is_favorite'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_recipe_is_favorite', table_name='recipe')
    op.drop_column('recipe', 'rating')
    op.drop_column('recipe', 'is_favorite')
