from datetime import datetime
import math
from ..excepciones import BusinessRuleError
from ..domain.categorias import Categoria
from ..schemas.categorias import CategoriaCreate, CategoriaPatch, CategoriaResponse
from ..schemas.common import PaginatedResponse
from ..repositories.categorias_repositorio import categoria_repositorio
from ..repositories.productos_repositorio import producto_repositorio

CAMPOS_ORDEN = {"nombre_categoria", "descripcion", "activa", "fecha_creacion", "fecha_actualizacion"}


class CategoriaService:
    def _a_categoria_response(self, categoria: Categoria) -> CategoriaResponse:
        return CategoriaResponse(
            id_categoria=categoria.id_categoria,
            nombre_categoria=categoria.nombre_categoria,
            descripcion=categoria.descripcion,
            activa=categoria.activa,
            fecha_creacion=categoria.fecha_creacion,
            fecha_actualizacion=categoria.fecha_actualizacion,
            cantidad_productos=producto_repositorio.contar_por_categoria(categoria.id_categoria),
        )

    def crear(self, categoria: CategoriaCreate) -> Categoria:
        entidad = Categoria(**categoria.model_dump())
        return categoria_repositorio.crear(entidad)

    def obtener_categorias( self,
                            activa: bool | None = None,
                            nombre: str | None = None,
                            ordenar_por: str = "nombre_categoria",
                            direccion: str = "asc",
                            pagina: int = 1,
                            limite: int = 20) -> PaginatedResponse[CategoriaResponse]:
        if ordenar_por not in CAMPOS_ORDEN:
            raise BusinessRuleError(f"El campo '{ordenar_por}' no es válido para ordenar")

        filtradas = categoria_repositorio.obtener_todas()
        if activa is not None:
            filtradas = [c for c in filtradas if c.activa == activa]
        if nombre:
            filtradas = [c for c in filtradas if nombre.lower() in c.nombre_categoria.lower()]

        reverse = direccion == "desc"
        filtradas = sorted(filtradas, key=lambda c: getattr(c, ordenar_por), reverse=reverse)

        total = len(filtradas)
        total_paginas = math.ceil(total / limite) if total > 0 else 0
        inicio = (pagina - 1) * limite
        items = [self._a_categoria_response(c) for c in filtradas[inicio:inicio + limite]]

        return PaginatedResponse(items=items, total=total, pagina=pagina,
                                 limite=limite, total_paginas=total_paginas)

    def obtener_por_id(self, id_categoria: str) -> CategoriaResponse:
        return self._a_categoria_response(categoria_repositorio.obtener_por_id(id_categoria))

    def actualizar(self, id_categoria: str, datos: CategoriaPatch) -> CategoriaResponse:
        entidad = categoria_repositorio.obtener_por_id(id_categoria)
        if datos.nombre_categoria is not None:
            entidad.nombre_categoria = datos.nombre_categoria
        if datos.descripcion is not None:
            entidad.descripcion = datos.descripcion
        if datos.activa is not None:
            entidad.activa = datos.activa
        entidad.fecha_actualizacion = datetime.now()
        categoria_repositorio.actualizar(id_categoria, entidad)
        return self._a_categoria_response(entidad)

    def eliminar(self, id_categoria: str) -> None:
        return categoria_repositorio.eliminar(id_categoria)


categoria_service = CategoriaService()
