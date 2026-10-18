from datetime import datetime
import math
from sqlalchemy.orm import Session
from ..excepciones import BusinessRuleError
from ..domain.productos import Producto
from ..schemas.productos_schemas import ProductoCreate, ProductoPatch, ProductoResponse
from ..schemas.common import PaginatedResponse
from ..repositories.categorias_repositorio import categoria_repositorio
from ..repositories.productos_repositorio import producto_repositorio

CAMPOS_ORDEN = {"nombre_producto", "descripcion", "stock", "stock_minimo",
                "id_categoria", "precio", "fecha_creacion", "fecha_actualizacion"}


class ProductoService:
    def _a_producto_response(self, producto: Producto) -> ProductoResponse:
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

    def crear(self, bd: Session, datos: ProductoCreate) -> Producto:
        categoria_repositorio.obtener_por_id(bd, datos.id_categoria)
        entidad = Producto(**datos.model_dump())
        return producto_repositorio.crear(bd, entidad)

    def obtener_productos(self,
                          bd: Session,
                          id_categoria: str | None = None,
                          nombre: str | None = None,
                          ordenar_por: str = "nombre_producto",
                          direccion: str = "asc",
                          pagina: int = 1,
                          limite: int = 20) -> PaginatedResponse[ProductoResponse]:
        if ordenar_por not in CAMPOS_ORDEN:
            raise BusinessRuleError(f"El campo '{ordenar_por}' no es válido para ordenar")

        filtrados = producto_repositorio.obtener_todos(bd)
        if id_categoria is not None:
            filtrados = [p for p in filtrados if p.id_categoria == id_categoria]
        if nombre:
            filtrados = [p for p in filtrados if nombre.lower() in p.nombre_producto.lower()]

        reverse = direccion == "desc"
        filtrados = sorted(filtrados, key=lambda p: getattr(p, ordenar_por), reverse=reverse)

        total = len(filtrados)
        total_paginas = math.ceil(total / limite) if total > 0 else 0
        inicio = (pagina - 1) * limite
        items = [self._a_producto_response(p) for p in filtrados[inicio:inicio + limite]]

        return PaginatedResponse(items=items, total=total, pagina=pagina,
                                 limite=limite, total_paginas=total_paginas)

    def obtener_por_id(self, bd: Session, id_producto: str) -> ProductoResponse:
        return self._a_producto_response(producto_repositorio.obtener_por_id(bd, id_producto))

    def actualizar(self, bd: Session, id_producto: str, datos: ProductoPatch) -> ProductoResponse:
        entidad = producto_repositorio.obtener_por_id(bd, id_producto)
        if datos.nombre_producto is not None:
            entidad.nombre_producto = datos.nombre_producto
        if datos.descripcion is not None:
            entidad.descripcion = datos.descripcion
        if datos.stock is not None:
            entidad.stock = datos.stock
        if datos.stock_minimo is not None:
            entidad.stock_minimo = datos.stock_minimo
        if datos.id_categoria is not None:
            categoria_repositorio.obtener_por_id(bd, datos.id_categoria)
            entidad.id_categoria = datos.id_categoria
        if datos.precio is not None:
            entidad.precio = datos.precio
        entidad.fecha_actualizacion = datetime.now()
        return self._a_producto_response(producto_repositorio.actualizar(bd, id_producto, entidad))

    def eliminar(self, bd: Session, id_producto: str) -> None:
        return producto_repositorio.eliminar(bd, id_producto)


producto_service = ProductoService()
