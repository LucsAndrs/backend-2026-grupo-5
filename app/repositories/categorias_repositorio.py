from ..excepciones import ConflictError, ResourceNotFoundError
from ..domain.categorias import Categoria


class CategoriaRepositorio:
    def __init__(self):
        self._categorias: list[Categoria] = []

    def crear(self, entidad: Categoria) -> Categoria:
        if any(cat.nombre_categoria.lower() == entidad.nombre_categoria.lower() for cat in self._categorias):
            raise ConflictError(f"Ya existe una categoría con el nombre '{entidad.nombre_categoria}'")
        self._categorias.append(entidad)
        return entidad

    def obtener_todas(self) -> list[Categoria]:
        return self._categorias

    def obtener_por_id(self, id_categoria: str) -> Categoria:
        for categoria in self._categorias:
            if categoria.id_categoria == id_categoria:
                return categoria
        raise ResourceNotFoundError("No existe una categoría con el ID solicitado")

    def actualizar(self, id_categoria: str, entidad: Categoria) -> Categoria:
        for idx, categoria in enumerate(self._categorias):
            if categoria.id_categoria == id_categoria:
                self._categorias[idx] = entidad
                return self._categorias[idx]
        raise ResourceNotFoundError("No existe una categoría con el ID solicitado")

    def eliminar(self, id_categoria: str) -> None:
        for idx, categoria in enumerate(self._categorias):
            if categoria.id_categoria == id_categoria:
                self._categorias.pop(idx)
                return None
        raise ResourceNotFoundError("No existe una categoría con el ID solicitado")


categoria_repositorio = CategoriaRepositorio()
