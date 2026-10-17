from pydantic import BaseModel, Field
from datetime import date
from backend.domain.pago import EstadoPago

#DTO entrada
class CrearPago(BaseModel):
    id_venta: str
    monto: float = Field(gt=0, description="debe ser mayor a 0")
    metodo_pago: str = Field(min_length=3, max_length=30)

#DTO salida 
class PagoRespuesta(BaseModel):
    id_pago: str
    id_venta: str
    fecha_pago: date
    monto: float
    metodo_pago: str
    estado_pago: EstadoPago
