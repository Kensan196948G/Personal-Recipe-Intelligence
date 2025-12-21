"""Add recipe_name to shopping_list_item

Revision ID: add_recipe_name
Revises: add_shopping_list
Create Date: 2025-12-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_recipe_name'
down_revision: Union[str, Sequence[str], None] = 'add_image_status'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add recipe_name column to shopping_list_item."""
    with op.batch_alter_table('shopping_list_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('recipe_name', sa.String(255), nullable=True))


def downgrade() -> None:
    """Remove recipe_name column from shopping_list_item."""
    with op.batch_alter_table('shopping_list_item', schema=None) as batch_op:
        batch_op.drop_column('recipe_name')
