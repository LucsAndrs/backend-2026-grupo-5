from ..domain.categoria import Categoria

categorias: list[Categoria] = []

def crear_categoria(entidad: Categoria):
    categorias.append(entidad)
    return entidad

def obtener_categorias():
    return categorias

def obtener_categoriaporid(id_categoria: str):
    for categoria in categorias:
        if categoria.id_categoria == id_categoria:
            return categoria
    raise KeyError("Categoría no encontrada")

def actualizar_categoria(id_categoria: str, entidad: Categoria):
    for idx, categoria in enumerate(categorias):
        if categoria.id_categoria == id_categoria:
            categorias[idx] = entidad
            return categorias[idx]
    raise KeyError("Categoría no encontrada")

def eliminar_categoria(id_categoria: str):
    for idx, categoria in enumerate(categorias):
        if categoria.id_categoria == id_categoria:
            categorias.pop(idx)
            return {"message": "Categoria eliminada con exito"}
    raise KeyError("Categoría no encontrada")