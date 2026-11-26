"""garantiza un solo pago exitoso por venta

Revision ID: a1f2c3d4e5b6
Revises: d558a2aa70ae
Create Date: 2026-11-25 21:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1f2c3d4e5b6'
down_revision: Union[str, Sequence[str], None] = 'd558a2aa70ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "uq_pagos_id_venta_exitosa",
        "pagos",
        ["id_venta"],
        unique=True,
        sqlite_where=sa.text("estado_pago = 'exitoso'"),
        postgresql_where=sa.text("estado_pago = 'exitoso'"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("uq_pagos_id_venta_exitosa", table_name="pagos")
