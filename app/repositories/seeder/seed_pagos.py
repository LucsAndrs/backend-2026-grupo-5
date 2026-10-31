from datetime import date

from sqlalchemy.orm import Session

from app.models.pago_bd import PagoBD
from app.models.venta_bd import VentaBD


PAGOS = [
    ("demo-pago-001", "demo-venta-001", date(2026, 10, 1), 4600.0, "debito", "exitoso"),
    ("demo-pago-002", "demo-venta-002", date(2026, 10, 2), 3400.0, "credito", "exitoso"),
]


def seedear_pagos(bd: Session) -> int:
    ventas = {venta.id_venta: venta for venta in bd.query(VentaBD).all()}
    faltantes = sorted({fila[1] for fila in PAGOS if fila[1] not in ventas})
    if faltantes:
        raise ValueError(f"Primero ejecuta el seeder de ventas. Ventas faltantes: {faltantes}")

    existentes = {id_pago for (id_pago,) in bd.query(PagoBD.id_pago).all()}
    nuevos = [
        PagoBD(
            id_pago=id_pago,
            id_venta=id_venta,
            fecha_pago=fecha,
            monto=monto,
            metodo_pago=metodo,
            estado_pago=estado,
        )
        for id_pago, id_venta, fecha, monto, metodo, estado in PAGOS
        if id_pago not in existentes
    ]
    bd.add_all(nuevos)
    bd.flush()
    return len(nuevos)
