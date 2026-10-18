from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class CategoriaCreate(BaseModel):
    nombre_categoria: str = Field(max_length=50)
    descripcion: str = Field(max_length=255)
    activa: bool

class CategoriaPatch(BaseModel):
    nombre_categoria: Optional[str] = Field(default=None, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    activa: Optional[bool] = None

class CategoriaResponse(BaseModel):
    id_categoria: str
    nombre_categoria: str
    descripcion: str
    activa: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    cantidad_productos: int
