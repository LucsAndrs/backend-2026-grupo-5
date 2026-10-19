
import uuid
from datetime import date
from app.domain.pago import Pago, EstadoPago
from app.excepciones import ResourceNotFoundError, BusinessRuleError
from app.repositories.pago_repository import pago_repositorio
from app.repositories.venta_repositorio import venta_repositorio
from app.schemas.pago_schemas import CrearPago


def procesar_pago(datos: CrearPago) -> Pago:
    venta = venta_repositorio.obtener_por_id(datos.id_venta)

    if pago_repositorio.existe_pago_exitoso(datos.id_venta):
        raise BusinessRuleError("La venta ya se encuentra pagada")

    if round(datos.monto, 2) != round(venta.total, 2):
        raise BusinessRuleError(
            f"el monto debe ser igual al total de la venta ({venta.total})"
        )

    nuevo_pago = Pago(
        id_pago=str(uuid.uuid4()),
        id_venta=datos.id_venta,
        fecha_pago=date.today(),
        monto=datos.monto,
        metodo_pago=datos.metodo_pago,
        estado_pago=EstadoPago.EXITOSO
    )
    return pago_repositorio.guardar(nuevo_pago)


def obtener_pago(id_pago: str) -> Pago:
    pago = pago_repositorio.obtener_por_id(id_pago)
    if pago is None:
        raise ResourceNotFoundError(f"No existe un pago con el ID {id_pago}")
    return pago


def listar_pagos() -> list[Pago]:
    return pago_repositorio.listar()