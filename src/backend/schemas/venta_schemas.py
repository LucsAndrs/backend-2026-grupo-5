from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from backend.schemas.detalle_venta_create import DetalleVentaCreate, DetalleVentaResponse
from backend.schemas.pago_schemas import PagoResponse

class VentaCreate(BaseModel):
    cliente: str = Field(..., min_length=5, max_length=90)
    detalles: list[DetalleVentaCreate] = Field(..., min_length=1)

class VentaOut(BaseModel):
    id: str
    fecha_venta: date
    cliente: str
    total: float
    detalles: list[DetalleVentaResponse]
    pago: Optional[PagoResponse] = None