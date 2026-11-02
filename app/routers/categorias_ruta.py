from typing import Literal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from ..base_datos import obtener_bd
from ..schemas.categorias_schemas import CategoriaCreate, CategoriaPatch, CategoriaResponse
from ..domain.categorias import Categoria
from ..schemas.common import PaginatedResponse
from ..services.categorias_servicio import categoria_service

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.post("/", response_model=Categoria, status_code=status.HTTP_201_CREATED)
def crear_categoria(categoria: CategoriaCreate, bd: Session = Depends(obtener_bd)) -> Categoria:
    return categoria_service.crear(bd, categoria)


@router.get("/", response_model=PaginatedResponse[CategoriaResponse])
def obtener_categorias(activa: bool | None = None,
                       nombre: str | None = None,
                       ordenar_por: str = Query("nombre_categoria"),
                       direccion: Literal["asc", "desc"] = "asc",
                       pagina: int = Query(1, ge=1),
                       limite: int = Query(20, ge=1, le=100),
                       bd: Session = Depends(obtener_bd)) -> PaginatedResponse[CategoriaResponse]:
    return categoria_service.obtener_categorias(bd, activa=activa, nombre=nombre, ordenar_por=ordenar_por,
                                                direccion=direccion, pagina=pagina, limite=limite)


@router.get("/{id_categoria}", response_model=CategoriaResponse)
def obtener_categoria_por_id(id_categoria: str, bd: Session = Depends(obtener_bd)) -> CategoriaResponse:
    return categoria_service.obtener_por_id(bd, id_categoria)


@router.patch("/{id_categoria}", response_model=CategoriaResponse)
def actualizar_categoria(id_categoria: str, datos: CategoriaPatch, bd: Session = Depends(obtener_bd)) -> CategoriaResponse:
    return categoria_service.actualizar(bd, id_categoria, datos)


@router.delete("/{id_categoria}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(id_categoria: str, bd: Session = Depends(obtener_bd)) -> None:
    categoria_service.eliminar(bd, id_categoria)
