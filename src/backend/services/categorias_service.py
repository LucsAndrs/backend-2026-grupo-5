from ..domain.categoria import Categoria

categorias: list[Categoria] =  []

def crear_categoria(categoria: Categoria):
     categorias.append(categoria)
     return categoria
 
def obtener_categoria(id_categoria: str):
    for categoria in categorias:
        if categoria.id_categoria == id_categoria:
            return categoria
    raise KeyError("Categoría no encontrada")