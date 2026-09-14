import uuid
from datetime import date
from backend.domain.pago import Pago, EstadoPago
from backend.domain.excepciones import RecursoNoEncontradoError
from backend.repositories.pago_repository import pago_repositorio
from backend.repositories.venta_repository import obtener_por_id as obtener_venta_por_id
from backend.schemas.pago_schemas import PagoCreate

def procesar_pago(datos: PagoCreate) -> Pago:
    try:
        obtener_venta_por_id(datos.id_venta)
    except RecursoNoEncontradoError:
        raise ValueError(f"no existe una venta con el ID {datos.id_venta}")

    if pago_repositorio.existe_pago_exitoso(datos.id_venta):
        raise ValueError("la venta ya se encuentra pagada")

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
        raise ValueError(f"no existe un pago con el ID {id_pago}")
    return pago

def listar_pagos() -> list[Pago]:
    return pago_repositorio.listar()
