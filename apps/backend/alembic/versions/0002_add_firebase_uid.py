"""add firebase_uid to users

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-06

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Add the Firebase UID column to users."""
    op.add_column("users", sa.Column("firebase_uid", sa.String(128), nullable=True))
    op.create_unique_constraint("uq_users_firebase_uid", "users", ["firebase_uid"])


def downgrade() -> None:
    """Remove the Firebase UID column from users."""
    op.drop_constraint("uq_users_firebase_uid", "users", type_="unique")
    op.drop_column("users", "firebase_uid")
