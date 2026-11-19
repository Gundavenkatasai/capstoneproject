"""Add Google auth provider and google_id to users

Revision ID: 0003_add_google_auth_fields
Revises: 0002_refresh_token_family
Create Date: 2026-11-19 22:36:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003_add_google_auth_fields'
down_revision: Union[str, None] = '0002_refresh_token_family'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('auth_provider', sa.String(length=50), nullable=False, server_default='local')
    )
    op.add_column(
        'users',
        sa.Column('google_id', sa.String(length=255), nullable=True)
    )
    op.create_index('idx_users_google_id', 'users', ['google_id'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_users_google_id', table_name='users')
    op.drop_column('users', 'google_id')
    op.drop_column('users', 'auth_provider')
