"""Make grievance_id nullable on grievance_evidence and create tracking sequence

Revision ID: 0004_grievance_lifecycle
Revises: 0003_add_google_auth_fields
Create Date: 2026-11-19 23:26:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0004_grievance_lifecycle'
down_revision: Union[str, None] = '0003_add_google_auth_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Make grievance_id nullable so evidence can be uploaded before complaint final submission
    op.alter_column(
        'grievance_evidence',
        'grievance_id',
        existing_type=sa.String(length=30),
        nullable=True
    )

    # 2. Create grievance tracking sequence for atomic GRV-YYYY-XXXXX generation
    op.execute("CREATE SEQUENCE IF NOT EXISTS grievance_tracking_seq START WITH 10001 INCREMENT BY 1;")


def downgrade() -> None:
    op.execute("DROP SEQUENCE IF EXISTS grievance_tracking_seq;")
    op.alter_column(
        'grievance_evidence',
        'grievance_id',
        existing_type=sa.String(length=30),
        nullable=False
    )
