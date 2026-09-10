from datetime import datetime
from ..domain.categoria import Categoria
from ..schemas.categoria import CategoriaCreate, CategoriaPatch
from ..repositories.categoria_repositorie import (crear_categoria as repo_crear_categoria,
                                                  obtener_categorias as repo_obtener_categorias,
                                                  obtener_categoriaporid as repo_obtener_categoriaporid,
                                                  actualizar_categoria as repo_actualizar_categoria,
                                                  eliminar_categoria as repo_eliminar_categoria)


def crear_categoria(categoria: CategoriaCreate):
    entidad = Categoria(**categoria.model_dump())
    return repo_crear_categoria(entidad)


def obtener_categorias():
    return repo_obtener_categorias()


def obtener_categoriaporid(id_categoria: str):
    return repo_obtener_categoriaporid(id_categoria)


def actualizar_categoria(id_categoria: str, datos: CategoriaPatch):
    entidad = obtener_categoriaporid(id_categoria)
    if datos.nombre_categoria is not None:
        entidad.nombre_categoria = datos.nombre_categoria
    if datos.descripcion is not None:
        entidad.descripcion = datos.descripcion
    if datos.activa is not None:
        entidad.activa = datos.activa
    entidad.fecha_actualizacion = datetime.now()
    return repo_actualizar_categoria(id_categoria, entidad)


def eliminar_categoria(id_categoria: str):
    return repo_eliminar_categoria(id_categoria)