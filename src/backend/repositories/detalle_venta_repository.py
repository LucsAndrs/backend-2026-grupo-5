from backend.domain.detalleventa import DetalleVenta
from typing import List, Optional

class DetalleVentaRepository:
    def __init__(self):
        self._datos: dict[str, DetalleVenta] = {}

    def guardar(self, detalle: DetalleVenta) -> DetalleVenta:
        self._datos[detalle.id_detalle] = detalle
        return detalle
    
    def obtener_por_id(self, id_detalle: str) -> Optional[DetalleVenta]:
        return self._datos.get(id_detalle)

    def obtener_todos(self) -> List[DetalleVenta]:
        return list(self._datos.values())