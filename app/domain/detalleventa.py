from dataclasses import dataclass, field
import uuid

@dataclass
class DetalleVenta:
    id_producto: str
    id_venta: str
    cantidad_producto:  int
    subtotal: int
    precio_unitario: int
    iva: float
    descuento: float
    id_detalle:  str = field(default_factory=lambda: str(uuid.uuid4()))