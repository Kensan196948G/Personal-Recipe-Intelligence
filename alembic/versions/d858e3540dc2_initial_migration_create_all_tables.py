"""Initial migration - create all tables

Revision ID: d858e3540dc2
Revises:
Create Date: 2025-12-11 13:31:35.318468

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'd858e3540dc2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  """Upgrade schema."""
  op.create_table('recipe',
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('servings', sa.Integer(), nullable=True),
    sa.Column('prep_time_minutes', sa.Integer(), nullable=True),
    sa.Column('cook_time_minutes', sa.Integer(), nullable=True),
    sa.Column('source_url', sa.String(), nullable=True),
    sa.Column('source_type', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
  )
  with op.batch_alter_table('recipe', schema=None) as batch_op:
    batch_op.create_index(batch_op.f('ix_recipe_title'), ['title'], unique=False)

  op.create_table('source',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('url_pattern', sa.String(), nullable=True),
    sa.Column('scraper_config', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
  )
  with op.batch_alter_table('source', schema=None) as batch_op:
    batch_op.create_index(batch_op.f('ix_source_name'), ['name'], unique=False)

  op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
  )
  with op.batch_alter_table('tag', schema=None) as batch_op:
    batch_op.create_index(batch_op.f('ix_tag_name'), ['name'], unique=True)

  op.create_table('ingredient',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('name_normalized', sa.String(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('unit', sa.String(), nullable=True),
    sa.Column('note', sa.String(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ),
    sa.PrimaryKeyConstraint('id')
  )
  with op.batch_alter_table('ingredient', schema=None) as batch_op:
    batch_op.create_index(batch_op.f('ix_ingredient_name'), ['name'], unique=False)
    batch_op.create_index(batch_op.f('ix_ingredient_name_normalized'), ['name_normalized'], unique=False)

  op.create_table('recipetag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('id')
  )

  op.create_table('step',
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ),
    sa.PrimaryKeyConstraint('id')
  )


def downgrade() -> None:
  """Downgrade schema."""
  op.drop_table('step')
  op.drop_table('recipetag')
  with op.batch_alter_table('ingredient', schema=None) as batch_op:
    batch_op.drop_index(batch_op.f('ix_ingredient_name_normalized'))
    batch_op.drop_index(batch_op.f('ix_ingredient_name'))

  op.drop_table('ingredient')
  with op.batch_alter_table('tag', schema=None) as batch_op:
    batch_op.drop_index(batch_op.f('ix_tag_name'))

  op.drop_table('tag')
  with op.batch_alter_table('source', schema=None) as batch_op:
    batch_op.drop_index(batch_op.f('ix_source_name'))

  op.drop_table('source')
  with op.batch_alter_table('recipe', schema=None) as batch_op:
    batch_op.drop_index(batch_op.f('ix_recipe_title'))

  op.drop_table('recipe')
