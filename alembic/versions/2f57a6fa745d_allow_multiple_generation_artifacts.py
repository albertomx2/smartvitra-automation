"""allow multiple generation artifacts

Revision ID: 2f57a6fa745d
Revises: c731f57aa8df
Create Date: 2026-08-23 13:49:13.439694

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "2f57a6fa745d"
down_revision: str | Sequence[str] | None = "c731f57aa8df"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
