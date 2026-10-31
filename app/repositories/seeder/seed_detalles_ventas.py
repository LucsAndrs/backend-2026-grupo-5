from sqlalchemy.orm import Session

from app.models.detalle_venta_db import DetalleVentaBD
from app.models.producto_bd import ProductoBD
from app.models.venta_bd import VentaBD


DETALLES = [
    ("demo-detalle-001", "demo-venta-001", "demo-arroz", 2),
    ("demo-detalle-002", "demo-venta-001", "demo-jugo", 1),
    ("demo-detalle-003", "demo-venta-002", "demo-arroz", 1),
    ("demo-detalle-004", "demo-venta-002", "demo-jugo", 1),
]


def seedear_detalles_ventas(bd: Session) -> int:
    ventas = {venta.id_venta: venta for venta in bd.query(VentaBD).all()}
    productos = {producto.id_producto: producto for producto in bd.query(ProductoBD).all()}
    ids_faltantes_venta = sorted({fila[1] for fila in DETALLES if fila[1] not in ventas})
    ids_faltantes_producto = sorted({fila[2] for fila in DETALLES if fila[2] not in productos})
    if ids_faltantes_venta or ids_faltantes_producto:
        raise ValueError(
            "Primero ejecuta los seeders de ventas y productos. "
            f"Ventas faltantes: {ids_faltantes_venta}; productos faltantes: {ids_faltantes_producto}"
        )

    existentes = {id_detalle for (id_detalle,) in bd.query(DetalleVentaBD.id_detalle).all()}
    nuevos = []
    for id_detalle, id_venta, id_producto, cantidad in DETALLES:
        if id_detalle in existentes:
            continue
        producto = productos[id_producto]
        nuevos.append(
            DetalleVentaBD(
                id_detalle=id_detalle,
                id_venta=id_venta,
                id_producto=id_producto,
                cantidad_producto=cantidad,
                precio_unitario=producto.precio,
                subtotal=cantidad * producto.precio,
                iva=0.0,
                descuento=0.0,
            )
        )
    bd.add_all(nuevos)
    bd.flush()
    return len(nuevos)
