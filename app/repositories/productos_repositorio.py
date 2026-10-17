from ..excepciones import ConflictError, ResourceNotFoundError
from ..domain.productos import Producto


class ProductoRepositorio:
    def __init__(self):
        self._productos: list[Producto] = []

    def crear(self, entidad: Producto) -> Producto:
        if any(prod.nombre_producto.lower() == entidad.nombre_producto.lower() for prod in self._productos):
            raise ConflictError(f"Ya existe un producto con el nombre '{entidad.nombre_producto}'")
        self._productos.append(entidad)
        return entidad

    def obtener_todos(self) -> list[Producto]:
        return self._productos

    def obtener_por_id(self, id_producto: str) -> Producto:
        for producto in self._productos:
            if producto.id_producto == id_producto:
                return producto
        raise ResourceNotFoundError("No existe un producto con el ID solicitado")

    def actualizar(self, id_producto: str, entidad: Producto) -> Producto:
        for idx, producto in enumerate(self._productos):
            if producto.id_producto == id_producto:
                self._productos[idx] = entidad
                return self._productos[idx]
        raise ResourceNotFoundError("No existe un producto con el ID solicitado")

    def eliminar(self, id_producto: str) -> None:
        for idx, producto in enumerate(self._productos):
            if producto.id_producto == id_producto:
                self._productos.pop(idx)
                return None
        raise ResourceNotFoundError("No existe un producto con el ID solicitado")

    def contar_por_categoria(self, id_categoria: str) -> int:
        return sum(1 for producto in self._productos if producto.id_categoria == id_categoria)


producto_repositorio = ProductoRepositorio()
