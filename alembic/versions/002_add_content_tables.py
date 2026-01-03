"""Add content tables for CMS

Revision ID: 002
Revises: 001
Create Date: 2024-12-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create content tables for CMS."""
    # Posts table
    op.create_table(
        'posts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('excerpt', sa.String(300), nullable=False),
        sa.Column('author', sa.String(100), nullable=False, server_default='Diego'),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_pillar', sa.String(50), nullable=False),
        sa.Column('target_level', sa.String(50), nullable=False),
        sa.Column('tags', postgresql.ARRAY(sa.String(50)), nullable=True),
        sa.Column('required_level', sa.Integer(), nullable=True),
        sa.Column('required_item', sa.String(100), nullable=True),
        sa.Column('challenge_text', sa.Text(), nullable=True),
        sa.Column('read_xp', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('quest_id', sa.String(100), nullable=True),
        sa.Column('meta_description', sa.String(160), nullable=True),
        sa.Column('og_image', sa.Text(), nullable=True),
        sa.Column('published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reading_time', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_posts_slug', 'posts', ['slug'], unique=True)
    op.create_index('ix_posts_published', 'posts', ['published'])

    # Quests table
    op.create_table(
        'quests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quest_id', sa.String(100), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('quest_type', sa.String(50), nullable=False),
        sa.Column('options', postgresql.ARRAY(sa.String(500)), nullable=True),
        sa.Column('correct_answer', sa.Text(), nullable=True),
        sa.Column('xp_reward', sa.Integer(), nullable=False),
        sa.Column('item_reward', sa.String(100), nullable=True),
        sa.Column('host_post_slug', sa.String(255), nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=False, server_default='easy'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_quests_quest_id', 'quests', ['quest_id'], unique=True)
    op.create_index('ix_quests_host_post_slug', 'quests', ['host_post_slug'])

    # Items table
    op.create_table(
        'items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_id', sa.String(100), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.String(200), nullable=False),
        sa.Column('icon', sa.String(255), nullable=False),
        sa.Column('rarity', sa.String(20), nullable=False, server_default='common'),
        sa.Column('flavor_text', sa.String(150), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_items_item_id', 'items', ['item_id'], unique=True)

    # Desktop icons table
    op.create_table(
        'desktop_icons',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('icon_id', sa.String(100), nullable=False),
        sa.Column('label', sa.String(20), nullable=False),
        sa.Column('icon', sa.String(255), nullable=False),
        sa.Column('position_x', sa.Integer(), nullable=False),
        sa.Column('position_y', sa.Integer(), nullable=False),
        sa.Column('window_type', sa.String(50), nullable=False),
        sa.Column('window_id', sa.String(100), nullable=True),
        sa.Column('external_url', sa.Text(), nullable=True),
        sa.Column('window_config', postgresql.JSONB(), nullable=True),
        sa.Column('required_level', sa.Integer(), nullable=True),
        sa.Column('required_item', sa.String(100), nullable=True),
        sa.Column('visible', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_desktop_icons_icon_id', 'desktop_icons', ['icon_id'], unique=True)

    # Desktop settings table
    op.create_table(
        'desktop_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(50), nullable=False, server_default='default'),
        sa.Column('grid_size', sa.Integer(), nullable=False, server_default='80'),
        sa.Column('icon_spacing', sa.Integer(), nullable=False, server_default='16'),
        sa.Column('start_position_x', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('start_position_y', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_desktop_settings_key', 'desktop_settings', ['key'], unique=True)

    # Window contents table
    op.create_table(
        'window_contents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('window_id', sa.String(100), nullable=False),
        sa.Column('title', sa.String(50), nullable=False),
        sa.Column('icon', sa.String(255), nullable=True),
        sa.Column('default_width', sa.Integer(), nullable=False, server_default='600'),
        sa.Column('default_height', sa.Integer(), nullable=False, server_default='400'),
        sa.Column('singleton', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('closable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('minimizable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('maximizable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('required_level', sa.Integer(), nullable=True),
        sa.Column('required_item', sa.String(100), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_window_contents_window_id', 'window_contents', ['window_id'], unique=True)


def downgrade() -> None:
    """Drop content tables."""
    op.drop_table('window_contents')
    op.drop_table('desktop_settings')
    op.drop_table('desktop_icons')
    op.drop_table('items')
    op.drop_table('quests')
    op.drop_table('posts')
