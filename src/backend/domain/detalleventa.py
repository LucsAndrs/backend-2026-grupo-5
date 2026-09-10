from dataclasses import dataclass

@dataclass
class DetalleVenta:
    id_detalle:  str
    id_producto: str
    cantidad_producto:  int
    subtotal: int
    precio_unitario: int
    iva: float
    descuento: float
