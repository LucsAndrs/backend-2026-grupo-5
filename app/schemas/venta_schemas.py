from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.detalle_venta_create import DetalleVentaCreate, DetalleVentaResponse
from app.schemas.pago_schemas import PagoRespuesta

class VentaCreada(BaseModel):
    cliente: str = Field(..., min_length=3, max_length=90)
    detalles: list[DetalleVentaCreate] = Field(..., min_length=1)

class VentaRespuesta(BaseModel):
    id_venta: str
    fecha_venta: date
    cliente: str
    total: float
    detalles: list[DetalleVentaResponse]
    pago: Optional[PagoRespuesta] = None