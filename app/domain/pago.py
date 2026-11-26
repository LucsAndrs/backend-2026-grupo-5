from dataclasses import dataclass, field
from enum import Enum
from datetime import date
import uuid


class EstadoPago(str, Enum):
    PENDIENTE = "pendiente"
    EXITOSO = "exitoso"
    RECHAZADO = "rechazado"


class MetodoPago(str, Enum):
    DEBITO = "debito"
    CREDITO = "credito"


@dataclass
class Pago:
    id_venta: str
    fecha_pago: date
    monto: float
    metodo_pago: MetodoPago
    estado_pago: EstadoPago
    id_pago: str = field(default_factory=lambda: str(uuid.uuid4()))
