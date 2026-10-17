from typing import List
from app.domain.detalleventa import DetalleVenta
from app.repositories.venta_repository import venta_repositorio
from app.excepciones import ResourceNotFoundError

class DetalleVentaService:
    def obtener_detalles_por_venta(self, id_venta: str) -> List[DetalleVenta]:
        venta = venta_repositorio.obtener_por_id(id_venta)
        return venta.detalles

    def obtener_detalle_especifico(self, id_venta: str, id_detalle: str) -> DetalleVenta:
        venta = venta_repositorio.obtener_por_id(id_venta)
        for detalle in venta.detalles:
            if detalle.id_detalle == id_detalle:
                return detalle
        raise ResourceNotFoundError(f"El detalle {id_detalle} no existe en la venta {id_venta}")