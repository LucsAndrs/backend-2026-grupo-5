from pydantic import BaseModel
from datetime import date

class Categoria(BaseModel):
    id_categoria = str
    nombre_categoria = str
    descripcion = str
    fecha_creacion = date
    activa = bool