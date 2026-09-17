from datetime import datetime
import math
from ..core.exceptions import BusinessRuleError
from ..domain.productos import Producto
from ..schemas.productos import ProductoCreate, ProductoPatch, ProductoResponse
from ..schemas.common import PaginatedResponse
from ..repositories.categorias_repositorio import obtener_categoria_por_id as repo_obtener_categoria_por_id
from ..repositories.productos_repositorio import (crear_producto as repo_crear_producto,
                                                  obtener_productos as repo_obtener_productos,
                                                  obtener_producto_por_id as repo_obtener_producto_por_id,
                                                  actualizar_producto as repo_actualizar_producto,
                                                  eliminar_producto as repo_eliminar_producto)

CAMPOS_ORDEN = {"nombre_producto", "descripcion", "stock", "stock_minimo",
                "id_categoria", "precio", "fecha_creacion", "fecha_actualizacion"}


def _a_producto_response(producto: Producto) -> ProductoResponse:
    return ProductoResponse(
        id_producto=producto.id_producto,
        nombre_producto=producto.nombre_producto,
        descripcion=producto.descripcion,
        stock=producto.stock,
        stock_minimo=producto.stock_minimo,
        id_categoria=producto.id_categoria,
        precio=producto.precio,
        fecha_creacion=producto.fecha_creacion,
        fecha_actualizacion=producto.fecha_actualizacion,
    )


def crear_producto(datos: ProductoCreate) -> Producto:
    repo_obtener_categoria_por_id(datos.id_categoria)
    entidad = Producto(**datos.model_dump())
    return repo_crear_producto(entidad)


def obtener_productos(id_categoria: str | None = None,
                      nombre: str | None = None,
                      ordenar_por: str = "nombre_producto",
                      direccion: str = "asc",
                      pagina: int = 1,
                      limite: int = 20) -> PaginatedResponse[ProductoResponse]:
    if ordenar_por not in CAMPOS_ORDEN:
        raise BusinessRuleError(f"El campo '{ordenar_por}' no es válido para ordenar")

    filtrados = repo_obtener_productos()
    if id_categoria is not None:
        filtrados = [p for p in filtrados if p.id_categoria == id_categoria]
    if nombre:
        filtrados = [p for p in filtrados if nombre.lower() in p.nombre_producto.lower()]

    reverse = direccion == "desc"
    filtrados = sorted(filtrados, key=lambda p: getattr(p, ordenar_por), reverse=reverse)

    total = len(filtrados)
    total_paginas = math.ceil(total / limite) if total > 0 else 0
    inicio = (pagina - 1) * limite
    items = [_a_producto_response(p) for p in filtrados[inicio:inicio + limite]]

    return PaginatedResponse(items=items, total=total, pagina=pagina,
                             limite=limite, total_paginas=total_paginas)


def obtener_producto_por_id(id_producto: str) -> ProductoResponse:
    return _a_producto_response(repo_obtener_producto_por_id(id_producto))


def actualizar_producto(id_producto: str, datos: ProductoPatch) -> ProductoResponse:
    entidad = repo_obtener_producto_por_id(id_producto)
    if datos.nombre_producto is not None:
        entidad.nombre_producto = datos.nombre_producto
    if datos.descripcion is not None:
        entidad.descripcion = datos.descripcion
    if datos.stock is not None:
        entidad.stock = datos.stock
    if datos.stock_minimo is not None:
        entidad.stock_minimo = datos.stock_minimo
    if datos.id_categoria is not None:
        repo_obtener_categoria_por_id(datos.id_categoria)
        entidad.id_categoria = datos.id_categoria
    if datos.precio is not None:
        entidad.precio = datos.precio
    entidad.fecha_actualizacion = datetime.now()
    return _a_producto_response(repo_actualizar_producto(id_producto, entidad))


def eliminar_producto(id_producto: str) -> None:
    return repo_eliminar_producto(id_producto)