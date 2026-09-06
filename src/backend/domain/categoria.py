from pydantic import BaseModel, Field
from datetime import date
import uuid

class CategoriaCreate(BaseModel):
    nombre_categoria : str
    descripcion : str
    fecha_creacion : date
    activa : bool
    
class Categoria(CategoriaCreate):
    id_categoria : str = Field(default_factory=lambda: str(uuid.uuid4()))