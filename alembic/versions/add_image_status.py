"""add image_status to recipe

Revision ID: add_image_status
Revises: add_source_id
Create Date: 2025-12-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_image_status'
down_revision: Union[str, None] = 'add_source_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add image_status column to recipe table"""
    op.add_column('recipe', sa.Column('image_status', sa.String(), nullable=True))


def downgrade() -> None:
    """Remove image_status column from recipe table"""
    op.drop_column('recipe', 'image_status')
