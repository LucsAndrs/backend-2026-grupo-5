from pydantic import BaseModel
from datetime import date

class Venta(BaseModel):
    id_venta: str
    fecha_venta: date
    total: float
    cliente: str