"""add task quality scores

Revision ID: 20260511_0002
Revises: 20260510_0001
Create Date: 2026-05-11 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260511_0002"
down_revision: Union[str, Sequence[str], None] = "20260510_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("task_executions", sa.Column("reasoning_quality_score", sa.Float(), nullable=True))
    op.add_column("task_executions", sa.Column("schema_validity_score", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("task_executions", "schema_validity_score")
    op.drop_column("task_executions", "reasoning_quality_score")
