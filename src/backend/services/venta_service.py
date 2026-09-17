import math
import uuid
from backend.domain.venta import Venta
from backend.domain.detalleventa import DetalleVenta
from backend.schemas.venta_schemas import VentaCreate
from backend.core.exceptions import BusinessRuleError
from backend.core.exceptions import ConflictError
from backend.schemas.common import PaginatedResponse
from datetime import date

from backend.repositories.productos_repositorio import(
    obtener_producto_por_id as obtener_producto,
    actualizar_producto as repo_actualizar_producto,
)
from backend.repositories.venta_repository import (
    crear_venta as repo_crear_venta,
    obtener_por_id as repo_obtener_por_id,
    listar_todas as repo_listar_todas,
    eliminar_venta as repo_eliminar_venta,
)
from backend.repositories.pago_repository import pago_repositorio

def calcular_total(venta: Venta):
    total = 0
    for detalle in venta.detalles:
        total = total + detalle.subtotal
    venta.total = total
    return total

CAMPOS_ORDEN = {"cliente", "total", "fecha_venta"}

def agregar_detalle(venta: Venta, detalle: DetalleVenta):
    if detalle.cantidad_producto <= 0:
        raise BusinessRuleError("La cantidad de producto debe ser mayor a cero")
    venta.detalles.append(detalle)
    calcular_total(venta)

def crear_venta(datos: VentaCreate):
    venta = Venta(cliente=datos.cliente, fecha_venta=date.today())
    for detalle_data in datos.detalles:
        producto = obtener_producto(detalle_data.id_producto)
        if detalle_data.cantidad_producto > producto.stock:
            raise BusinessRuleError(
                f"Stock insuficiente para '{producto.nombre_producto}':"
                f" Disponible '{producto.stock}', solicitado'{detalle_data.cantidad_producto}'"
            )
        detalle = DetalleVenta(
            id_detalle= str(uuid.uuid4),
            id_producto= producto.id_producto,
            id_venta= venta.id_venta,
            cantidad_producto= detalle_data.cantidad_producto,
            precio_unitario= producto.precio,
            subtotal= detalle_data.cantidad_producto * producto.precio,
            iva= 0.0,
            descuento= 0.0,
        )
        agregar_detalle(venta, detalle)
        producto.stock -= detalle_data.cantidad_producto
        repo_actualizar_producto(producto.id_producto, producto)
    return repo_crear_venta(venta)

def obtener_venta(id_venta: str):
    return repo_obtener_por_id(id_venta)

def eliminar_venta(id_venta: str):
    obtener_venta(id_venta)
    if pago_repositorio.existe_pago_exitoso(id_venta):
        raise ConflictError("No se puede eliminar una venta que ya fue pagada")
    return repo_eliminar_venta(id_venta)

def listar_venta(cliente: str = None, ordenar_por: str = None, direccion: str = "asc",
                 pagina: int = 1, limite: int = 20):
    if ordenar_por is not None and ordenar_por not in CAMPOS_ORDEN:
        raise BusinessRuleError(f"El campo '{ordenar_por}' no es valido para ordenar")
    ventas = repo_listar_todas()

    if cliente:
        ventas_filtradas = []
        for v in ventas:
            if v.cliente == cliente:
                ventas_filtradas.append(v)
        ventas = ventas_filtradas

    if ordenar_por:
        reverse = direccion == "desc"
        ventas = sorted(ventas, key=lambda v: getattr(v, ordenar_por), reverse=reverse)

    total = len(ventas)
    if total == 0:
        total_paginas = 0
    else:
        total_paginas = math.ceil(total / limite)
    inicio = (pagina - 1) * limite
    fin = inicio + limite
    ventas_pagina = ventas[inicio:fin]

    return PaginatedResponse(
        items= ventas_pagina,
        total= total,
        pagina= pagina,
        limite= limite,
        total_paginas= total_paginas,
    )

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