from typing import List
from app.domain.detalleventa import DetalleVenta
from sqlalchemy.orm import Session
from app.repositories.detalle_venta_repositorio import detalle_venta_repositorio

class DetalleVentaServicio:
    def obtener_detalles_por_venta(
        self,
        bd: Session,
        id_venta: str,
    ) -> List[DetalleVenta]:
        return detalle_venta_repositorio.obtener_todos_de_una_venta(bd, id_venta)

    def obtener_detalle_especifico(
        self,
        bd: Session,
        id_venta: str,
        id_detalle: str,
    ) -> DetalleVenta:
        return detalle_venta_repositorio.obtener_por_id(bd, id_venta, id_detalle)
