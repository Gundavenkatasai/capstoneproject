"""Add family tracking and client metadata to refresh_tokens

Revision ID: 0002_refresh_token_family
Revises: 0001_initial_schema
Create Date: 2026-11-19 20:46:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0002_refresh_token_family'
down_revision: Union[str, None] = '0001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'refresh_tokens',
        sa.Column('family_id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()'))
    )
    op.add_column(
        'refresh_tokens',
        sa.Column('user_agent', sa.String(length=255), nullable=True)
    )
    op.add_column(
        'refresh_tokens',
        sa.Column('ip_address', sa.String(length=50), nullable=True)
    )
    op.create_index('idx_refresh_tokens_family_id', 'refresh_tokens', ['family_id'])


def downgrade() -> None:
    op.drop_index('idx_refresh_tokens_family_id', table_name='refresh_tokens')
    op.drop_column('refresh_tokens', 'ip_address')
    op.drop_column('refresh_tokens', 'user_agent')
    op.drop_column('refresh_tokens', 'family_id')
