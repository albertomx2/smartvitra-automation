"""Link generated proposals to Odoo draft quotations.

Revision ID: b712d5b48713
Revises: 64d8b721c590
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b712d5b48713"
down_revision: str | Sequence[str] | None = "64d8b721c590"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("generation_jobs", sa.Column("odoo_partner_id", sa.Integer()))
    op.add_column("generation_jobs", sa.Column("odoo_partner_created", sa.Boolean()))
    op.add_column("generation_jobs", sa.Column("odoo_sale_order_id", sa.Integer()))
    op.add_column(
        "generation_jobs", sa.Column("odoo_sale_order_name", sa.String(100))
    )


def downgrade() -> None:
    op.drop_column("generation_jobs", "odoo_sale_order_name")
    op.drop_column("generation_jobs", "odoo_sale_order_id")
    op.drop_column("generation_jobs", "odoo_partner_id")
    op.drop_column("generation_jobs", "odoo_partner_created")
