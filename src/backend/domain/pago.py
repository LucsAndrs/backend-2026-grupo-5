from pydantic import BaseModel
from enum import Enum
from datetime import date

class EstadoPago(str, Enum):
    PENDIENTE = "pendiente"
    EXITOSO = "exitoso"
    RECHAZADO = "rechazado"

class Pago(BaseModel):
    id_pago: str
    fecha_pago: date
    monto: float
    metodo_pago: str
    estado_pago: EstadoPago