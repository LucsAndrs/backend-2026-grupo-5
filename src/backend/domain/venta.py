from dataclasses import dataclass, field
from datetime import date
import uuid

from backend.domain.detalleventa import DetalleVenta

@dataclass
class Venta:
    id_venta: str = field(default_factory=lambda: str(uuid.uuid4()))
    cliente: str
    fecha_venta: date
    total: float = 0.0
    detalles: list[DetalleVenta] = field(default_factory=list)