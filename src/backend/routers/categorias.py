from typing import Literal
from fastapi import APIRouter, Query, status
from ..schemas.categorias import CategoriaCreate, CategoriaPatch
from ..domain.categorias import Categoria
from ..schemas.common import PaginatedResponse
from ..services.categorias_service import (crear_categoria as crear_categoria_service,
                                           actualizar_categoria as actualizar_categoria_service,
                                           obtener_categoria_por_id as obtener_categoria_por_id_service,
                                           obtener_categorias as obtener_categorias_service,
                                           eliminar_categoria as eliminar_categoria_service)

router = APIRouter(prefix="/categorias")


@router.post("/", response_model=Categoria, status_code=status.HTTP_201_CREATED)
def crear_categoria(categoria: CategoriaCreate) -> Categoria:
    return crear_categoria_service(categoria)


@router.get("/", response_model=PaginatedResponse[Categoria])
def obtener_categorias(activa: bool | None = None,
                       nombre: str | None = None,
                       ordenar_por: str = Query("nombre_categoria"),
                       direccion: Literal["asc", "desc"] = "asc",
                       pagina: int = Query(1, ge=1),
                       limite: int = Query(20, ge=1, le=100)) -> PaginatedResponse[Categoria]:
    return obtener_categorias_service(activa=activa, nombre=nombre, ordenar_por=ordenar_por,
                                      direccion=direccion, pagina=pagina, limite=limite)


@router.get("/{id_categoria}", response_model=Categoria)
def obtener_categoria_por_id(id_categoria: str) -> Categoria:
    return obtener_categoria_por_id_service(id_categoria)


@router.patch("/{id_categoria}", response_model=Categoria)
def actualizar_categoria(id_categoria: str, datos: CategoriaPatch) -> Categoria:
    return actualizar_categoria_service(id_categoria, datos)


@router.delete("/{id_categoria}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(id_categoria: str) -> None:
    eliminar_categoria_service(id_categoria)