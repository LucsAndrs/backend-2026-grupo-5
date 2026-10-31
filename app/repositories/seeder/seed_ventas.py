from datetime import date

from sqlalchemy.orm import Session

from app.models.venta_modelos import VentaBD


VENTAS = [
    ("demo-venta-001", "Cliente Demo Uno", date(2026, 10, 1), 4600.0),
    ("demo-venta-002", "Cliente Demo Dos", date(2026, 10, 2), 3400.0),
]


def seedear_ventas(bd: Session) -> int:
    existentes = {id_venta for (id_venta,) in bd.query(VentaBD.id_venta).all()}
    nuevas = [
        VentaBD(
            id_venta=id_venta,
            cliente=cliente,
            fecha_venta=fecha,
            total=total,
        )
        for id_venta, cliente, fecha, total in VENTAS
        if id_venta not in existentes
    ]
    bd.add_all(nuevas)
    bd.flush()
    return len(nuevas)
