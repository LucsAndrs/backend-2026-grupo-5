from ..core.exceptions import ConflictError, ResourceNotFoundError
from ..domain.productos import Producto

productos: list[Producto] = []


def crear_producto(entidad: Producto) -> Producto:
    if any(prod.nombre_producto.lower() == entidad.nombre_producto.lower() for prod in productos):
        raise ConflictError(f"Ya existe un producto con el nombre '{entidad.nombre_producto}'")
    productos.append(entidad)
    return entidad


def obtener_productos() -> list[Producto]:
    return productos


def obtener_producto_por_id(id_producto: str) -> Producto:
    for producto in productos:
        if producto.id_producto == id_producto:
            return producto
    raise ResourceNotFoundError("No existe un producto con el ID solicitado")


def actualizar_producto(id_producto: str, entidad: Producto) -> Producto:
    for idx, producto in enumerate(productos):
        if producto.id_producto == id_producto:
            productos[idx] = entidad
            return productos[idx]
    raise ResourceNotFoundError("No existe un producto con el ID solicitado")


def eliminar_producto(id_producto: str) -> None:
    for idx, producto in enumerate(productos):
        if producto.id_producto == id_producto:
            productos.pop(idx)
            return None
    raise ResourceNotFoundError("No existe un producto con el ID solicitado")


def contar_productos_por_categoria(id_categoria: str) -> int:
    return sum(1 for producto in productos if producto.id_categoria == id_categoria)