from typing import Literal
from fastapi import APIRouter, Query, status
from ..schemas.productos import ProductoCreate, ProductoPatch
from ..domain.productos import Producto
from ..schemas.common import PaginatedResponse
from ..services.productos_service import (crear_producto as crear_producto_service,
                                          actualizar_producto as actualizar_producto_service,
                                          obtener_producto_por_id as obtener_producto_por_id_service,
                                          obtener_productos as obtener_productos_service,
                                          eliminar_producto as eliminar_producto_service)

router = APIRouter(prefix="/productos")


@router.post("/", response_model=Producto, status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate) -> Producto:
    return crear_producto_service(datos)


@router.get("/", response_model=PaginatedResponse[Producto])
def obtener_productos(id_categoria: str | None = None,
                      nombre: str | None = None,
                      ordenar_por: str = Query("nombre_producto"),
                      direccion: Literal["asc", "desc"] = "asc",
                      pagina: int = Query(1, ge=1),
                      limite: int = Query(20, ge=1, le=100)) -> PaginatedResponse[Producto]:
    return obtener_productos_service(id_categoria=id_categoria, nombre=nombre, ordenar_por=ordenar_por,
                                     direccion=direccion, pagina=pagina, limite=limite)


@router.get("/{id_producto}", response_model=Producto)
def obtener_producto_por_id(id_producto: str) -> Producto:
    return obtener_producto_por_id_service(id_producto)


@router.patch("/{id_producto}", response_model=Producto)
def actualizar_producto(id_producto: str, datos: ProductoPatch) -> Producto:
    return actualizar_producto_service(id_producto, datos)


@router.delete("/{id_producto}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(id_producto: str) -> None:
    eliminar_producto_service(id_producto)