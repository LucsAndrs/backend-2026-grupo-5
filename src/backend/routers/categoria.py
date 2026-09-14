from typing import Literal
from fastapi import APIRouter, Query, status
from ..schemas.categoria import CategoriaCreate, CategoriaPatch
from ..domain.categoria import Categoria
from ..schemas.common import PaginatedResponse
from ..services.categorias_service import (crear_categoria, actualizar_categoria,
                                           obtener_categoriaporid, obtener_categorias,
                                           eliminar_categoria)

router = APIRouter(prefix="/categoria")

@router.post("/", response_model=Categoria, status_code=status.HTTP_201_CREATED)
def crear_cat(categoria: CategoriaCreate):
    return crear_categoria(categoria)

@router.get("/", response_model=PaginatedResponse[Categoria])
def obtener_cat(activa: bool | None = None,
                nombre: str | None = None,
                ordenar_por: str = Query("nombre_categoria"),
                direccion: Literal["asc", "desc"] = "asc",
                pagina: int = Query(1, ge=1),
                limite: int = Query(20, ge=1, le=100)):
    return obtener_categorias(activa=activa, nombre=nombre, ordenar_por=ordenar_por,
                              direccion=direccion, pagina=pagina, limite=limite)

@router.get("/{id_categoria}", response_model=Categoria)
def obtener_catporid(id_categoria: str):
    return obtener_categoriaporid(id_categoria)

@router.patch("/{id_categoria}", response_model=Categoria)
def actualizar_cat(id_categoria: str, datos: CategoriaPatch):
    return actualizar_categoria(id_categoria, datos)

@router.delete("/{id_categoria}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cat(id_categoria: str):
    eliminar_categoria(id_categoria)