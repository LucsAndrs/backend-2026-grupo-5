from pydantic import BaseModel

class DetalleVenta(BaseModel):
    id_detalle:  str
    cantidad_producto:  int
    subtotal: int
    precio_unitario: int
    iva: float
    descuento: float
