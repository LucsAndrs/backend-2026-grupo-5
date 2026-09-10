from pydantic import BaseModel
from typing import Optional

class CategoriaCreate(BaseModel):
    nombre_categoria: str
    descripcion: str
    activa: bool
    
class CategoriaPatch(BaseModel):
    nombre_categoria: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None
    