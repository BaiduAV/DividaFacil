"""Add password reset token fields

Revision ID: 07e59571203c
Revises: b229d2cff548
Create Date: 2025-09-24 23:29:54.023247

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "07e59571203c"
down_revision: Union[str, Sequence[str], None] = "b229d2cff548"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema (idempotent)."""
    bind = op.get_bind()
    inspector = inspect(bind)
    existing = {c["name"] for c in inspector.get_columns("users")}
    if "reset_token" not in existing:
        op.add_column("users", sa.Column("reset_token", sa.String(), nullable=True))
    if "reset_token_expiry" not in existing:
        op.add_column("users", sa.Column("reset_token_expiry", sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema (conditional)."""
    bind = op.get_bind()
    inspector = inspect(bind)
    existing = {c["name"] for c in inspector.get_columns("users")}
    if "reset_token_expiry" in existing:
        op.drop_column("users", "reset_token_expiry")
    if "reset_token" in existing:
        op.drop_column("users", "reset_token")
