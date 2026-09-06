from fastapi import APIRouter
from ..schemas.categoria import CategoriaCreate
from ..domain.categoria import Categoria
from ..services.categorias_service import crear_categoria

router = APIRouter(prefix="/categoria")

@router.post("/", response_model=Categoria)
def crear_cat(categoria: CategoriaCreate):
    return crear_categoria(categoria)