from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = 'd558a2aa70ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ventas', sa.Column('numero_boleta', sa.String(length=32), nullable=True))
    op.create_index(op.f('ix_ventas_numero_boleta'), 'ventas', ['numero_boleta'], unique=False)

    conexion = op.get_bind()
    filas = conexion.execute(
        sa.text('SELECT id_venta, fecha_venta FROM ventas ORDER BY fecha_venta, id_venta')
    ).fetchall()

    usados = set()
    for id_venta, fecha_venta in filas:
        dia = fecha_venta.strftime('%Y%m%d') if hasattr(fecha_venta, 'strftime') else str(fecha_venta)[:10].replace('-', '')
        base = f"BOL-{dia}-{str(id_venta).upper().replace('-', '')[:8]}"
        numero = base
        sufijo = 1
        while numero in usados:
            numero = f"{base}-{sufijo}"
            sufijo += 1
        usados.add(numero)
        conexion.execute(
            sa.text('UPDATE ventas SET numero_boleta = :numero WHERE id_venta = :id_venta'),
            {'numero': numero, 'id_venta': id_venta},
        )

    with op.batch_alter_table('ventas') as batch_op:
        batch_op.alter_column(
            'numero_boleta',
            existing_type=sa.String(length=32),
            nullable=False,
        )
        batch_op.create_unique_constraint('uq_ventas_numero_boleta', ['numero_boleta'])


def downgrade() -> None:
    with op.batch_alter_table('ventas') as batch_op:
        batch_op.drop_constraint('uq_ventas_numero_boleta', type_='unique')
        batch_op.alter_column(
            'numero_boleta',
            existing_type=sa.String(length=32),
            nullable=True,
        )
    op.drop_index(op.f('ix_ventas_numero_boleta'), table_name='ventas')
    op.drop_column('ventas', 'numero_boleta')
