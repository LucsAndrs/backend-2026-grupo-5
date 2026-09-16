from backend.domain.detalleventa import DetalleVenta
from typing import List, Optional
from backend.repositories.venta_repository import obtener_por_id

class DetalleVentaRepository:
    def obtener_todos_de_una_venta(self, id_venta: str) -> List[DetalleVenta]:
        venta = obtener_por_id(id_venta)
        return venta.detalles
    
    def obtener_por_id(self, id_venta: str, id_detalle: str) -> Optional[DetalleVenta]:
        venta = obtener_por_id(id_venta)
        for detalle in venta.detalles:
            if detalle.id_detalle == id_detalle:
                return detalle
        return None