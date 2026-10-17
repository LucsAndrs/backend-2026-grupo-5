from app.domain.detalleventa import DetalleVenta
from typing import List, Optional
from app.repositories.venta_repository import venta_repositorio

class DetalleVentaRepositorio:
    def obtener_todos_de_una_venta(self, id_venta: str) -> List[DetalleVenta]:
        venta = venta_repositorio.obtener_por_id(id_venta)
        return venta.detalles
    
    def obtener_por_id(self, id_venta: str, id_detalle: str) -> Optional[DetalleVenta]:
        venta = venta_repositorio.obtener_por_id(id_venta)
        for detalle in venta.detalles:
            if detalle.id_detalle == id_detalle:
                return detalle
        return None