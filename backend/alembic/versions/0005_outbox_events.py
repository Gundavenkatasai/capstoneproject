"""Add transactional outbox events table

Revision ID: 0005_outbox_events
Revises: 0004_grievance_lifecycle
Create Date: 2026-11-20 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0005_outbox_events'
down_revision: Union[str, None] = '0004_grievance_lifecycle'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'outbox_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('aggregate_type', sa.String(length=50), nullable=False, server_default='grievance'),
        sa.Column('aggregate_id', sa.String(length=100), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('correlation_id', sa.String(length=100), nullable=True),
        sa.Column('error_details', sa.Text(), nullable=True),
        sa.Column('scheduled_for', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_index('idx_outbox_status_scheduled', 'outbox_events', ['status', 'scheduled_for'])
    op.create_index('idx_outbox_aggregate', 'outbox_events', ['aggregate_type', 'aggregate_id'])
    op.create_index('idx_outbox_correlation', 'outbox_events', ['correlation_id'])
    op.create_index('idx_outbox_created_at', 'outbox_events', ['created_at'])


def downgrade() -> None:
    op.drop_index('idx_outbox_created_at', table_name='outbox_events')
    op.drop_index('idx_outbox_correlation', table_name='outbox_events')
    op.drop_index('idx_outbox_aggregate', table_name='outbox_events')
    op.drop_index('idx_outbox_status_scheduled', table_name='outbox_events')
    op.drop_table('outbox_events')
