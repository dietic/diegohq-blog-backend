"""Initial migration - Create all tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables."""
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(30), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('xp', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('longest_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Refresh tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])

    # Inventory items table
    op.create_table(
        'inventory_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_id', sa.String(100), nullable=False),
        sa.Column('acquired_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'item_id', name='uq_user_item'),
    )
    op.create_index('ix_inventory_items_user_id', 'inventory_items', ['user_id'])
    op.create_index('ix_inventory_items_item_id', 'inventory_items', ['item_id'])

    # Quest progress table
    op.create_table(
        'quest_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quest_id', sa.String(100), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('answer_given', sa.Text(), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'quest_id', name='uq_user_quest'),
    )
    op.create_index('ix_quest_progress_user_id', 'quest_progress', ['user_id'])
    op.create_index('ix_quest_progress_quest_id', 'quest_progress', ['quest_id'])

    # Post progress table
    op.create_table(
        'post_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('post_slug', sa.String(255), nullable=False),
        sa.Column('has_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_unlocked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('unlocked_with_item', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'post_slug', name='uq_user_post'),
    )
    op.create_index('ix_post_progress_user_id', 'post_progress', ['user_id'])
    op.create_index('ix_post_progress_post_slug', 'post_progress', ['post_slug'])

    # Daily rewards table
    op.create_table(
        'daily_rewards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('claimed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('reward_type', sa.String(50), nullable=False),
        sa.Column('reward_value', sa.Integer(), nullable=False),
        sa.Column('streak_day', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_daily_rewards_user_id', 'daily_rewards', ['user_id'])

    # XP transactions table
    op.create_table(
        'xp_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('source_id', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_xp_transactions_user_id', 'xp_transactions', ['user_id'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('xp_transactions')
    op.drop_table('daily_rewards')
    op.drop_table('post_progress')
    op.drop_table('quest_progress')
    op.drop_table('inventory_items')
    op.drop_table('refresh_tokens')
    op.drop_table('users')
