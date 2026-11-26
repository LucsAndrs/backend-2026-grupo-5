from pydantic import BaseModel, ConfigDict

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

    model_config = ConfigDict(from_attributes=True)

class DetalleVentaConsulta(DetalleVentaRespuesta):
    id_venta: str