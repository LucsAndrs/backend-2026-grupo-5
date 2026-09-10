from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from backend.schemas.detalleventa import DetalleVentaCreate, DetalleVentaOut
from backend.schemas.pago import PagoOut

class VentaCreate(BaseModel):
    cliente: str = Field(..., min_length=5, max_length=90)
    detalles: list[DetalleVentaCreate] = Field(..., min_length=1)

class VentaOut(BaseModel):
    id: str
    fecha_venta: date
    cliente: str
    total: float
    detalles: list[DetalleVentaOut]
    pago: Optional[PagoOut] = []