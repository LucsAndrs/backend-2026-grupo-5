from backend.domain.venta import Venta

def generar_boleta(venta: Venta):
    items = []
    for detalle in venta.detalles:
        item = {
            "producto_id": detalle.producto_id,
            "cantidad": detalle.cantidad_producto,
            "precio_unitario": detalle.precio_unitario,
            "subtotal": detalle.subtotal,
        }
        items.append(item)

    boleta = {
        "id_venta": venta.id,
        "fecha_venta": venta.fecha_venta.isoformat(),
        "cliente": venta.cliente,
        "items": items,
        "total": venta.total
    }
    return boleta