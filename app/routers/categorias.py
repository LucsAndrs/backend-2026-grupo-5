from typing import Literal
from fastapi import APIRouter, Query, status
from ..schemas.categorias import CategoriaCreate, CategoriaPatch, CategoriaResponse
from ..domain.categorias import Categoria
from ..schemas.common import PaginatedResponse
from ..services.categorias_service import categoria_service

router = APIRouter(prefix="/categorias")


@router.post("/", response_model=Categoria, status_code=status.HTTP_201_CREATED)
def crear_categoria(categoria: CategoriaCreate) -> Categoria:
    return categoria_service.crear(categoria)


@router.get("/", response_model=PaginatedResponse[CategoriaResponse])
def obtener_categorias(activa: bool | None = None,
                       nombre: str | None = None,
                       ordenar_por: str = Query("nombre_categoria"),
                       direccion: Literal["asc", "desc"] = "asc",
                       pagina: int = Query(1, ge=1),
                       limite: int = Query(20, ge=1, le=100)) -> PaginatedResponse[CategoriaResponse]:
    return categoria_service.obtener_categorias(activa=activa, nombre=nombre, ordenar_por=ordenar_por,
                                                direccion=direccion, pagina=pagina, limite=limite)


@router.get("/{id_categoria}", response_model=CategoriaResponse)
def obtener_categoria_por_id(id_categoria: str) -> CategoriaResponse:
    return categoria_service.obtener_por_id(id_categoria)


@router.patch("/{id_categoria}", response_model=CategoriaResponse)
def actualizar_categoria(id_categoria: str, datos: CategoriaPatch) -> CategoriaResponse:
    return categoria_service.actualizar(id_categoria, datos)


@router.delete("/{id_categoria}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(id_categoria: str) -> None:
    categoria_service.eliminar(id_categoria)
