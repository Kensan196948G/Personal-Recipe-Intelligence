"""add image fields to recipe

Revision ID: add_image_fields
Revises: b48d7f4eb20b
Create Date: 2025-12-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'add_image_fields'
down_revision: Union[str, None] = 'b48d7f4eb20b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add image_url and image_path columns to recipe table"""
    # Add image_url column
    op.add_column('recipe', sa.Column('image_url', sa.String(), nullable=True))

    # Add image_path column
    op.add_column('recipe', sa.Column('image_path', sa.String(), nullable=True))


def downgrade() -> None:
    """Remove image_url and image_path columns from recipe table"""
    op.drop_column('recipe', 'image_path')
    op.drop_column('recipe', 'image_url')
