from fastapi import APIRouter
from ..schemas.categoria import CategoriaCreate, CategoriaPatch
from ..domain.categoria import Categoria
from ..services.categorias_service import (crear_categoria, actualizar_categoria,
                                           obtener_categoriaporid, obtener_categorias,
                                           eliminar_categoria)

router = APIRouter(prefix="/categoria")

@router.post("/", response_model= Categoria)
def crear_cat(categoria: CategoriaCreate):
    return crear_categoria(categoria)

@router.get("/", response_model= list[Categoria])
def obtener_cat():
    return obtener_categorias()    

@router.get("/{id_categoria}", response_model= Categoria)
def obtener_catporid(id_categoria: str):
    return obtener_categoriaporid(id_categoria)

@router.patch("/{id_categoria}", response_model= Categoria)
def actualizar_cat(id_categoria: str, datos: CategoriaPatch):
    return actualizar_categoria(id_categoria, datos)

@router.delete("/{id_categoria}")
def eliminar_cat(id_categoria: str):
    return eliminar_categoria(id_categoria)