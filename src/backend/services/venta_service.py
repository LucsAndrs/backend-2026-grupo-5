from backend.domain.venta import Venta
from backend.domain.detalleventa import DetalleVenta
from backend.schemas.venta_schemas import VentaCreate
from datetime import date
from backend.repositories.venta_repository import (
    crear_venta as repo_crear_venta,
    obtener_por_id as repo_obtener_por_id,
    listar_todas as repo_listar_todas,
)

def calcular_total(venta: Venta):
    total = 0
    for detalle in venta.detalles:
        total = total + detalle.subtotal
    venta.total = total
    return total

def agregar_detalle(venta: Venta, detalle: DetalleVenta):
    if detalle.cantidad_producto <= 0:
        raise ValueError("La cantidad de producto debe ser mayor a cero")
    venta.detalles.append(detalle)
    calcular_total(venta)

def crear_venta(datos: VentaCreate):
    venta = Venta(cliente=datos.cliente, fecha_venta=date.today())
    for detalle_data in datos.detalles:
        detalle = DetalleVenta(**detalle_data.model_dump())
        agregar_detalle(venta, detalle)
    return repo_crear_venta(venta)

def obtener_venta(id_venta: str):
    return repo_obtener_por_id(id_venta)

def listar_venta():
    return repo_listar_todas()

def generar_boleta(venta: Venta):
    items = []
    for detalle in venta.detalles:
        items.append({
            "producto_id": detalle.id_producto,
            "cantidad": detalle.cantidad_producto,
            "precio_unitario": detalle.precio_unitario,
            "subtotal": detalle.subtotal,
        })

    return {
        "id_venta": venta.id_venta,
        "fecha_venta": venta.fecha_venta.isoformat(),
        "cliente": venta.cliente,
        "items": items,
        "total": venta.total,
    }