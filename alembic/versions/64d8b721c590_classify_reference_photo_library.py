"""classify reference photo library

Revision ID: 64d8b721c590
Revises: 03592778fdee
Create Date: 2026-09-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "64d8b721c590"
down_revision: str | Sequence[str] | None = "03592778fdee"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("reference_photos", sa.Column("element_type", sa.String(50)))
    op.add_column("reference_photos", sa.Column("opening_system", sa.String(50)))
    op.add_column(
        "reference_photos",
        sa.Column("leaf_configuration", sa.String(50)),
    )
    op.add_column("reference_photos", sa.Column("content_sha256", sa.String(64)))
    op.add_column("reference_photos", sa.Column("source_path", sa.String(500)))
    op.add_column("reference_photos", sa.Column("width_px", sa.Integer()))
    op.add_column("reference_photos", sa.Column("height_px", sa.Integer()))
    op.add_column(
        "reference_photos",
        sa.Column("quality_score", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_unique_constraint(
        "uq_reference_photos_content_sha256",
        "reference_photos",
        ["content_sha256"],
    )
    op.alter_column("reference_photos", "quality_score", server_default=None)


def downgrade() -> None:
    op.drop_constraint(
        "uq_reference_photos_content_sha256",
        "reference_photos",
        type_="unique",
    )
    for column in (
        "quality_score",
        "height_px",
        "width_px",
        "source_path",
        "content_sha256",
        "leaf_configuration",
        "opening_system",
        "element_type",
    ):
        op.drop_column("reference_photos", column)
