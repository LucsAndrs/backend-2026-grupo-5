from app.domain.detalleventa import DetalleVenta
from typing import List
from sqlalchemy.orm import Session
from app.excepciones import ResourceNotFoundError
from app.models.detalle_venta_modelos import DetalleVentaBD

class DetalleVentaRepositorio:
    def obtener_todos_de_una_venta(
        self,
        bd: Session,
        id_venta: str,
    ) -> List[DetalleVenta]:
        detalles_bd = (
            bd.query(DetalleVentaBD)
            .filter(DetalleVentaBD.id_venta == id_venta)
            .all()
        )

        return [self._a_entidad(detalle) for detalle in detalles_bd]
    
    def obtener_por_id(
        self,
        bd: Session,
        id_venta: str,
        id_detalle: str,
    ) -> DetalleVenta:
        detalle_bd = (
            bd.query(DetalleVentaBD)
            .filter(
                DetalleVentaBD.id_venta == id_venta,
                DetalleVentaBD.id_detalle == id_detalle,
            )
            .first()
        )

        if detalle_bd is None:
            raise ResourceNotFoundError(
                f"El detalle {id_detalle} no existe en la venta {id_venta}"
            )

        return self._a_entidad(detalle_bd)

    def _a_entidad(self, detalle_bd: DetalleVentaBD) -> DetalleVenta:
        return DetalleVenta(
            id_detalle=detalle_bd.id_detalle,
            id_producto=detalle_bd.id_producto,
            id_venta=detalle_bd.id_venta,
            cantidad_producto=detalle_bd.cantidad_producto,
            subtotal=detalle_bd.subtotal,
            precio_unitario=detalle_bd.precio_unitario,
            iva=detalle_bd.iva,
            descuento=detalle_bd.descuento,
        )

detalle_venta_repositorio = DetalleVentaRepositorio()