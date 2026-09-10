from dataclasses import dataclass, field
from datetime import date

from backend.domain.detalleventa import DetalleVenta

@dataclass
class Venta:
    id: str
    fecha_venta: date
    cliente: str
    total: float
    detalles: list[DetalleVenta] = field(default_factory=list)

    def agregar_detalle(self, detalle: DetalleVenta):
        if detalle.cantidad_producto <= 0:
            raise ValueError("La cantidad de producto debe ser mayor a cero")
        self.detalles.append(detalle)
        self.total = self.calcular_total()

    def calcular_total(self):
        total = 0
        for detalle in self.detalles:
            total = total + detalle.subtotal
        return total