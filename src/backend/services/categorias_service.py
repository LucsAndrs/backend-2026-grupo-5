from ..domain.categoria import Categoria
from ..schemas.categoria import CategoriaCreate

categorias: list[Categoria] =  []

def crear_categoria(categoria: CategoriaCreate):
     entidad = Categoria(**categoria.model_dump())
     categorias.append(entidad)
     return entidad
 
def obtener_categoria(id_categoria: str):
    for categoria in categorias:
        if categoria.id_categoria == id_categoria:
            return categoria
    raise KeyError("Categoría no encontrada")