"""Add contact submissions table

Revision ID: 003
Revises: 002
Create Date: 2024-12-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create contact_submissions table."""
    op.create_table(
        'contact_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_replied', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reply_message', sa.Text(), nullable=True),
        sa.Column('replied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('replied_by', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_contact_submissions_is_read', 'contact_submissions', ['is_read'])
    op.create_index('ix_contact_submissions_created_at', 'contact_submissions', ['created_at'])


def downgrade() -> None:
    """Drop contact_submissions table."""
    op.drop_table('contact_submissions')
