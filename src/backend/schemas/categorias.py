from datetime import datetime
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

class CategoriaResponse(BaseModel):
    id_categoria: str
    nombre_categoria: str
    descripcion: str
    activa: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    cantidad_productos: int
    