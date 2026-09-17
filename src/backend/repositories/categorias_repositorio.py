from ..core.exceptions import ConflictError, ResourceNotFoundError
from ..domain.categorias import Categoria

categorias: list[Categoria] = []


def crear_categoria(entidad: Categoria) -> Categoria:
    if any(cat.nombre_categoria.lower() == entidad.nombre_categoria.lower() for cat in categorias):
        raise ConflictError(f"Ya existe una categoría con el nombre '{entidad.nombre_categoria}'")
    categorias.append(entidad)
    return entidad


def obtener_categorias() -> list[Categoria]:
    return categorias


def obtener_categoria_por_id(id_categoria: str) -> Categoria:
    for categoria in categorias:
        if categoria.id_categoria == id_categoria:
            return categoria
    raise ResourceNotFoundError("No existe una categoría con el ID solicitado")


def actualizar_categoria(id_categoria: str, entidad: Categoria) -> Categoria:
    for idx, categoria in enumerate(categorias):
        if categoria.id_categoria == id_categoria:
            categorias[idx] = entidad
            return categorias[idx]
    raise ResourceNotFoundError("No existe una categoría con el ID solicitado")


def eliminar_categoria(id_categoria: str) -> None:
    for idx, categoria in enumerate(categorias):
        if categoria.id_categoria == id_categoria:
            categorias.pop(idx)
            return None
    raise ResourceNotFoundError("No existe una categoría con el ID solicitado")