from pydantic import BaseModel

class DetalleVentaCrear(BaseModel):
    id_producto: str
    cantidad_producto: int

class DetalleVentaRespuesta(BaseModel):
    id_detalle: str
    id_producto: str
    cantidad_producto: int
    precio_unitario: int
    subtotal: int
    iva: float
    descuento: float

    class Config:
        from_attributes = True