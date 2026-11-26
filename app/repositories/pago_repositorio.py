from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.pago import EstadoPago, MetodoPago, Pago
from app.excepciones import ConflictError
from app.models.pago_modelos import PagoBD


MENSAJE_PAGO_DUPLICADO = "La venta ya se encuentra pagada"


def _es_pago_exitoso_duplicado(exc: IntegrityError) -> bool:
    detalle = str(exc.orig) if exc.orig is not None else str(exc)
    detalle = detalle.lower()
    return (
        "uq_pagos_id_venta_exitosa" in detalle
        or "unique constraint failed: pagos.id_venta" in detalle
    )


class PagoRepositorio:
    def guardar(self, bd: Session, pago: Pago) -> Pago:
        pago_bd = PagoBD(
            id_pago=pago.id_pago,
            id_venta=pago.id_venta,
            fecha_pago=pago.fecha_pago,
            monto=pago.monto,
            metodo_pago=pago.metodo_pago.value,
            estado_pago=pago.estado_pago.value,
        )
        try:
            bd.add(pago_bd)
            bd.commit()
            bd.refresh(pago_bd)
        except IntegrityError as exc:
            bd.rollback()
            if _es_pago_exitoso_duplicado(exc):
                raise ConflictError(MENSAJE_PAGO_DUPLICADO) from exc
            raise
        return self._a_entidad(pago_bd)

    def obtener_por_id(self, bd: Session, id_pago: str) -> Pago | None:
        pago_bd = (
            bd.query(PagoBD)
            .filter(PagoBD.id_pago == id_pago)
            .first()
        )
        return self._a_entidad(pago_bd) if pago_bd else None

    def listar(self, bd: Session) -> list[Pago]:
        pagos_bd = bd.query(PagoBD).all()
        return [self._a_entidad(pago_bd) for pago_bd in pagos_bd]

    def obtener_por_venta(self, bd: Session, id_venta: str) -> list[Pago]:
        pagos_bd = (
            bd.query(PagoBD)
            .filter(PagoBD.id_venta == id_venta)
            .all()
        )
        return [self._a_entidad(pago_bd) for pago_bd in pagos_bd]

    def existe_pago_exitoso(self, bd: Session, id_venta: str) -> bool:
        return (
            bd.query(PagoBD)
            .filter(
                PagoBD.id_venta == id_venta,
                PagoBD.estado_pago == EstadoPago.EXITOSO.value,
            )
            .first()
            is not None
        )

    @staticmethod
    def _a_entidad(pago_bd: PagoBD) -> Pago:
        return Pago(
            id_pago=pago_bd.id_pago,
            id_venta=pago_bd.id_venta,
            fecha_pago=pago_bd.fecha_pago,
            monto=pago_bd.monto,
            metodo_pago=MetodoPago(pago_bd.metodo_pago),
            estado_pago=EstadoPago(pago_bd.estado_pago),
        )


pago_repositorio = PagoRepositorio()