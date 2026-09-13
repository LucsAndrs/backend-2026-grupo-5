from backend.domain.venta import Venta
from backend.domain.detalleventa import DetalleVenta
from backend.schemas.venta_schemas import VentaCreate
from datetime import date

from backend.repositories.venta_repository import (
    crear_venta as repo_crear_venta,
    obtener_por_id as repo_obtener_por_id,
    listar_todas as repo_listar_todas,
    eliminar_venta as repo_eliminar_venta,
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

def eliminar_venta(id_venta: str):
    return repo_eliminar_venta(id_venta)

def listar_venta(cliente: str = None, ordenar_por: str = None, direccion: str = "asc",
                 pagina: int = 1, limite: int = 20):
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
    total_paginas = (total + limite - 1) // limite if total > 0 else 0
    inicio = (pagina - 1) * limite
    fin = inicio + limite
    ventas_pagina = ventas[inicio:fin]

    return{
        "items": ventas_pagina,
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "total_paginas": total_paginas,
    }

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