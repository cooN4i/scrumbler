"""initial schema

Revision ID: dd3c68fa6484
Revises: None
Create Date: 2026-09-16 01:28:44.397243

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dd3c68fa6484"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    # 2. Create solves table
    op.create_table(
        "solves",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("raw_time_ms", sa.Integer(), nullable=False),
        sa.Column("penalty", sa.String(length=10), nullable=False),
        sa.Column("scramble", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_solves_id"), "solves", ["id"], unique=False)
    op.create_index(op.f("ix_solves_user_id"), "solves", ["user_id"], unique=False)
    op.create_index(op.f("ix_solves_created_at"), "solves", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_solves_created_at"), table_name="solves")
    op.drop_index(op.f("ix_solves_user_id"), table_name="solves")
    op.drop_index(op.f("ix_solves_id"), table_name="solves")
    op.drop_table("solves")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
