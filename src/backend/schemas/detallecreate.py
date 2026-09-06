from pydantic import BaseModel

class DetalleVentaCreate(BaseModel):
    id_producto: str
    cantidad_producto: int

class DetalleVentaResponse(BaseModel):
    id_detalle: str
    id_producto: str
    cantidad_producto: int
    precio_unitario: int
    subtotal: int
    iva: float
    descuento: float

    class Config:
        from_attributes = True