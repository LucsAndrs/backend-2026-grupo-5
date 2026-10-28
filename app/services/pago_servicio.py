import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.domain.pago import EstadoPago, Pago
from app.excepciones import BusinessRuleError, ResourceNotFoundError
from app.repositories.pago_repositorio import pago_repositorio
from app.repositories.venta_repositorio import venta_repositorio
from app.schemas.pago_schemas import CrearPago


def procesar_pago(bd: Session, datos: CrearPago) -> Pago:
    venta = venta_repositorio.obtener_por_id(bd, datos.id_venta)

    if pago_repositorio.existe_pago_exitoso(bd, datos.id_venta):
        raise BusinessRuleError("La venta ya se encuentra pagada")

    if round(datos.monto, 2) != round(venta.total, 2):
        raise BusinessRuleError(
            f"El monto debe ser igual al total de la venta ({venta.total})"
        )

    nuevo_pago = Pago(
        id_pago=str(uuid.uuid4()),
        id_venta=datos.id_venta,
        fecha_pago=date.today(),
        monto=datos.monto,
        metodo_pago=datos.metodo_pago,
        estado_pago=EstadoPago.EXITOSO,
    )
    return pago_repositorio.guardar(bd, nuevo_pago)


def obtener_pago(bd: Session, id_pago: str) -> Pago:
    pago = pago_repositorio.obtener_por_id(bd, id_pago)
    if pago is None:
        raise ResourceNotFoundError(f"No existe un pago con el ID {id_pago}")
    return pago


def listar_pagos(bd: Session) -> list[Pago]:
    return pago_repositorio.listar(bd)