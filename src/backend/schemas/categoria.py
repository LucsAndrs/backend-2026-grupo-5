from pydantic import BaseModel
from datetime import date

class CategoriaCreate(BaseModel):
    nombre_categoria: str
    descripcion: str
    fecha_creacion: date
    activa: bool