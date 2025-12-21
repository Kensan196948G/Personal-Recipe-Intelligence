"""Add shopping list tables

Revision ID: add_shopping_list
Revises: d858e3540dc2
Create Date: 2025-12-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_shopping_list'
down_revision: Union[str, Sequence[str], None] = 'd858e3540dc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create shopping list tables."""
    # shopping_list table
    op.create_table('shopping_list',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False, server_default='買い物リスト'),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # shopping_list_item table
    op.create_table('shopping_list_item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('shopping_list_id', sa.Integer(), nullable=False),
        sa.Column('recipe_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('note', sa.String(), nullable=True),
        sa.Column('is_checked', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['shopping_list_id'], ['shopping_list.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('shopping_list_item', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_shopping_list_item_name'), ['name'], unique=False)


def downgrade() -> None:
    """Drop shopping list tables."""
    op.drop_table('shopping_list_item')
    op.drop_table('shopping_list')
