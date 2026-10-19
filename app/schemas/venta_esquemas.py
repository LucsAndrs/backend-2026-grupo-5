from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.detalle_venta_esquema import DetalleVentaCrear, DetalleVentaRespuesta
from app.schemas.pago_schemas import PagoRespuesta

class VentaCreada(BaseModel):
    cliente: str = Field(..., min_length=3, max_length=90)
    detalles: list[DetalleVentaCrear] = Field(..., min_length=1)

class VentaRespuesta(BaseModel):
    id_venta: str
    fecha_venta: date
    cliente: str
    total: float
    detalles: list[DetalleVentaRespuesta]
    pago: Optional[PagoRespuesta] = None