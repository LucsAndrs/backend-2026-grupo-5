from sqlalchemy.orm import Session
from app.domain.venta import Venta
from app.domain.detalleventa import DetalleVenta
from app.excepciones import ResourceNotFoundError
from app.models.venta_bd import VentaBD
from app.models.detalle_venta_db import DetalleVentaBD

class VentaRepositorio:
    def crear_venta(self, bd: Session, venta: Venta) -> Venta:
        venta_bd = VentaBD(
            id_venta=venta.id_venta,
            cliente=venta.cliente,
            fecha_venta=venta.fecha_venta,
            total=venta.total
        )

        for d in venta.detalles:
            detalle_bd = DetalleVentaBD(
                id_detalle=d.id_detalle,
                id_producto=d.id_producto,
                id_venta=venta.id_venta,
                cantidad_producto=d.cantidad_producto,
                precio_unitario=d.precio_unitario,
                subtotal=d.subtotal,
                iva=getattr(d, "iva", 0.0),
                descuento=getattr(d, "descuento", 0.0)
            )
            venta_bd.detalles.append(detalle_bd)

        bd.add(venta_bd)
        bd.commit()
        bd.refresh(venta_bd)
        return venta

    def obtener_por_id(self, bd: Session, id_venta: str) -> Venta:
        venta_bd = bd.query(VentaBD).filter(VentaBD.id_venta == id_venta).first()
        if not venta_bd:
            raise ResourceNotFoundError(f"No existe una venta con el ID {id_venta}")

        detalles_bd = []
        if hasattr(venta_bd, "detalles") and venta_bd.detalles:
            for d in venta_bd.detalles:
                detalles_bd.append(
                    DetalleVenta(
                        id_detalle=d.id_detalle,
                        id_producto=d.id_producto,
                        id_venta=d.id_venta,
                        cantidad_producto=d.cantidad_producto,
                        precio_unitario=d.precio_unitario,
                        subtotal=d.subtotal,
                        iva=getattr(d, "iva", 0.0),
                        descuento=getattr(d, "descuento", 0.0)
                    )
                )

            return Venta(
                id_venta=venta_bd.id_venta,
                cliente=venta_bd.cliente,
                fecha_venta=venta_bd.fecha_venta,
                total=venta_bd.total,
                detalles=detalles_bd
            )

    def listar_todas(self, bd: Session) -> list[Venta]:
        ventas_bd = bd.query(VentaBD).all()
        return [self.obtener_por_id(bd, v.id_venta) for v in ventas_bd]

    def eliminar_venta(self, bd: Session, id_venta: str):
        venta_bd = bd.query(VentaBD).filter(VentaBD.id_venta == id_venta).first()
        if not venta_bd:
            raise ResourceNotFoundError(f"No existe una venta con el ID {id_venta}")
        bd.delete(venta_bd)
        bd.commit()

venta_repositorio = VentaRepositorio()