"""eliminar tabla alumnos (sobrante de crud_bd y crud_orm)

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-19 00:25:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # IF EXISTS: en una base de datos nueva (p. ej. en Docker) la tabla no existe.
    op.execute("DROP TABLE IF EXISTS alumnos")


def downgrade() -> None:
    """Downgrade schema."""
    # Recrea la tabla vacía (los datos borrados no se recuperan).
    op.create_table(
        "alumnos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=50), nullable=False),
        sa.Column("correo", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
