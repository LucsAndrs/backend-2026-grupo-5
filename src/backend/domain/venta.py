from dataclasses import dataclass, field
from datetime import date
import uuid

from backend.domain.detalleventa import DetalleVenta

@dataclass
class Venta:
    cliente: str
    fecha_venta: date
    total: float = 0.0
    id_venta: str = field(default_factory=lambda: str(uuid.uuid4()))
    detalles: list[DetalleVenta] = field(default_factory=list)