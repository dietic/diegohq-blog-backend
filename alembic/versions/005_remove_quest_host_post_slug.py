"""Remove host_post_slug from quests

Revision ID: 005
Revises: 004
Create Date: 2025-01-04 00:00:00.000000

Posts now reference quests via post.quest_id instead of quests referencing posts.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove host_post_slug column from quests table."""
    op.drop_index('ix_quests_host_post_slug', 'quests')
    op.drop_column('quests', 'host_post_slug')


def downgrade() -> None:
    """Re-add host_post_slug column to quests table."""
    op.add_column(
        'quests',
        sa.Column('host_post_slug', sa.String(255), nullable=False, server_default='')
    )
    op.create_index('ix_quests_host_post_slug', 'quests', ['host_post_slug'])
