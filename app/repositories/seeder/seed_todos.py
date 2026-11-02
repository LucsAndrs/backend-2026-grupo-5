"""Carga datos demo en orden de dependencias. Ejecutar desde la raíz:
python -m app.repositories.seeder.seed_todos
"""

from app.base_datos import SesionLocal
from app.models import categoria_modelos, detalle_venta_modelos, pago_modelos, producto_modelos, venta_modelos
from app.repositories.seeder.seed_categorias import seedear_categorias
from app.repositories.seeder.seed_detalles_ventas import seedear_detalles_ventas
from app.repositories.seeder.seed_pagos import seedear_pagos
from app.repositories.seeder.seed_productos import seedear_productos
from app.repositories.seeder.seed_ventas import seedear_ventas


def seedear_todo() -> dict[str, int]:
    bd = SesionLocal()
    try:
        resultados = {
            "categorias": seedear_categorias(bd),
            "productos": seedear_productos(bd),
            "ventas": seedear_ventas(bd),
            "detalles_ventas": seedear_detalles_ventas(bd),
            "pagos": seedear_pagos(bd),
        }
        bd.commit()
        return resultados
    except Exception:
        bd.rollback()
        raise
    finally:
        bd.close()


if __name__ == "__main__":
    insertados = seedear_todo()
    print("Registros nuevos insertados:")
    for entidad, cantidad in insertados.items():
        print(f"- {entidad}: {cantidad}")
