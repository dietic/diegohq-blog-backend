"""Add code quest support

Revision ID: 004
Revises: 003
Create Date: 2024-01-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add code quest support columns and tables."""
    # Add new columns to quests table for code quests
    op.add_column('quests', sa.Column('language', sa.String(50), nullable=True))
    op.add_column('quests', sa.Column('starter_code', sa.Text(), nullable=True))
    op.add_column('quests', sa.Column('ai_criteria', sa.Text(), nullable=True))
    op.add_column('quests', sa.Column('hint', sa.Text(), nullable=True))

    # Add new columns to quest_progress for tracking
    op.add_column('quest_progress', sa.Column('started_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('quest_progress', sa.Column('last_attempt_at', sa.DateTime(timezone=True), nullable=True))

    # Create quest_submissions table
    op.create_table(
        'quest_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quest_id', sa.String(100), nullable=False),
        sa.Column('submission_type', sa.String(50), nullable=False),
        sa.Column('code_submitted', sa.Text(), nullable=True),
        sa.Column('answer_submitted', sa.String(500), nullable=True),
        sa.Column('passed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_quest_submissions_user_id', 'quest_submissions', ['user_id'])
    op.create_index('ix_quest_submissions_quest_id', 'quest_submissions', ['quest_id'])


def downgrade() -> None:
    """Remove code quest support columns and tables."""
    op.drop_table('quest_submissions')

    op.drop_column('quest_progress', 'last_attempt_at')
    op.drop_column('quest_progress', 'started_at')

    op.drop_column('quests', 'hint')
    op.drop_column('quests', 'ai_criteria')
    op.drop_column('quests', 'starter_code')
    op.drop_column('quests', 'language')
