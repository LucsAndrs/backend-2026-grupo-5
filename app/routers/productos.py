from typing import Literal
from fastapi import APIRouter, Query, status
from ..schemas.productos import ProductoCreate, ProductoPatch, ProductoResponse
from ..domain.productos import Producto
from ..schemas.common import PaginatedResponse
from ..services.productos_service import producto_service

router = APIRouter(prefix="/productos")


@router.post("/", response_model=Producto, status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate) -> Producto:
    return producto_service.crear(datos)


@router.get("/", response_model=PaginatedResponse[ProductoResponse])
def obtener_productos(id_categoria: str | None = None,
                      nombre: str | None = None,
                      ordenar_por: str = Query("nombre_producto"),
                      direccion: Literal["asc", "desc"] = "asc",
                      pagina: int = Query(1, ge=1),
                      limite: int = Query(20, ge=1, le=100)) -> PaginatedResponse[ProductoResponse]:
    return producto_service.obtener_productos(id_categoria=id_categoria, nombre=nombre, ordenar_por=ordenar_por,
                                              direccion=direccion, pagina=pagina, limite=limite)


@router.get("/{id_producto}", response_model=ProductoResponse)
def obtener_producto_por_id(id_producto: str) -> ProductoResponse:
    return producto_service.obtener_por_id(id_producto)


@router.patch("/{id_producto}", response_model=ProductoResponse)
def actualizar_producto(id_producto: str, datos: ProductoPatch) -> ProductoResponse:
    return producto_service.actualizar(id_producto, datos)


@router.delete("/{id_producto}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(id_producto: str) -> None:
    producto_service.eliminar(id_producto)
