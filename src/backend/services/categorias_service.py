from datetime import datetime
import math
from ..core.exceptions import BusinessRuleError
from ..domain.categorias import Categoria
from ..schemas.categorias import CategoriaCreate, CategoriaPatch
from ..schemas.common import PaginatedResponse
from ..repositories.categorias_repositorio import (crear_categoria as repo_crear_categoria,
                                                   obtener_categorias as repo_obtener_categorias,
                                                   obtener_categoria_por_id as repo_obtener_categoria_por_id,
                                                   actualizar_categoria as repo_actualizar_categoria,
                                                   eliminar_categoria as repo_eliminar_categoria)

CAMPOS_ORDEN = {"nombre_categoria", "descripcion", "activa", "fecha_creacion", "fecha_actualizacion"}


def crear_categoria(categoria: CategoriaCreate) -> Categoria:
    entidad = Categoria(**categoria.model_dump())
    return repo_crear_categoria(entidad)


def obtener_categorias(activa: bool | None = None,
                       nombre: str | None = None,
                       ordenar_por: str = "nombre_categoria",
                       direccion: str = "asc",
                       pagina: int = 1,
                       limite: int = 20) -> PaginatedResponse[Categoria]:
    if ordenar_por not in CAMPOS_ORDEN:
        raise BusinessRuleError(f"El campo '{ordenar_por}' no es válido para ordenar")

    filtradas = repo_obtener_categorias()
    if activa is not None:
        filtradas = [c for c in filtradas if c.activa == activa]
    if nombre:
        filtradas = [c for c in filtradas if nombre.lower() in c.nombre_categoria.lower()]

    reverse = direccion == "desc"
    filtradas = sorted(filtradas, key=lambda c: getattr(c, ordenar_por), reverse=reverse)

    total = len(filtradas)
    total_paginas = math.ceil(total / limite) if total > 0 else 0
    inicio = (pagina - 1) * limite
    items = filtradas[inicio:inicio + limite]

    return PaginatedResponse(items=items, total=total, pagina=pagina,
                             limite=limite, total_paginas=total_paginas)


def obtener_categoria_por_id(id_categoria: str) -> Categoria:
    return repo_obtener_categoria_por_id(id_categoria)


def actualizar_categoria(id_categoria: str, datos: CategoriaPatch) -> Categoria:
    entidad = obtener_categoria_por_id(id_categoria)
    if datos.nombre_categoria is not None:
        entidad.nombre_categoria = datos.nombre_categoria
    if datos.descripcion is not None:
        entidad.descripcion = datos.descripcion
    if datos.activa is not None:
        entidad.activa = datos.activa
    entidad.fecha_actualizacion = datetime.now()
    return repo_actualizar_categoria(id_categoria, entidad)


def eliminar_categoria(id_categoria: str) -> None:
    return repo_eliminar_categoria(id_categoria)