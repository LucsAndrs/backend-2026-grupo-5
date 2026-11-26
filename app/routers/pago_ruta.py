from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.base_datos import obtener_bd
from app.schemas.common import ErrorResponse
from app.schemas.pago_schemas import CrearPago, PagoRespuesta
from app.services.pago_servicio import (
    listar_pagos,
    obtener_pago,
    procesar_pago,
)


router = APIRouter(prefix="/pagos", tags=["pagos"])

PAGO_EJEMPLO = {
    "id_pago": "9b2c7f41-6e5d-4a3b-9f80-1c2d3e4f5a6b",
    "id_venta": "d3f1c2a4-5b6e-4f7a-8c9d-0e1f2a3b4c5d",
    "fecha_pago": "2026-11-25",
    "monto": 2400,
    "metodo_pago": "debito",
    "estado_pago": "exitoso",
}


def _error_respuesta(code: str, message: str) -> dict:
    return {
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"error": {"code": code, "message": message, "details": []}}
            }
        },
    }


REGLA_NEGOCIO = _error_respuesta(
    "BUSINESS_RULE_VIOLATION", "El monto debe ser igual al total de la venta (100.0)"
)
NO_ENCONTRADO = _error_respuesta(
    "RESOURCE_NOT_FOUND", "No existe una venta con el ID solicitado"
)
CONFLICTO = _error_respuesta("CONFLICT", "La venta ya se encuentra pagada")
VALIDACION = _error_respuesta(
    "VALIDATION_ERROR", "Los datos no cumplen las validaciones del esquema"
)


@router.post(
    "",
    response_model=PagoRespuesta,
    status_code=201,
    summary="Procesar el pago de una venta",
    description=(
        "Registra un pago exitoso para una venta existente. "
        "El monto debe ser mayor a cero, tener máximo dos decimales y coincidir "
        "con el total de la venta. Solo se permite un pago exitoso por venta, "
        "incluso ante solicitudes simultáneas. "
        "El método de pago debe ser 'debito' o 'credito'."
    ),
    responses={
        201: {
            "description": "Pago registrado correctamente.",
            "content": {"application/json": {"example": PAGO_EJEMPLO}},
        },
        400: {
            **REGLA_NEGOCIO,
            "description": "El monto no coincide con el total de la venta.",
        },
        404: {**NO_ENCONTRADO, "description": "La venta asociada no existe."},
        409: {
            **CONFLICTO,
            "description": "La venta ya tiene un pago exitoso; el índice único lo garantiza.",
        },
        422: {
            **VALIDACION,
            "description": "El cuerpo no cumple el contrato de CrearPago.",
        },
    },
)
def post_pago(datos: CrearPago, bd: Session = Depends(obtener_bd)):
    return procesar_pago(bd, datos)


@router.get(
    "",
    response_model=list[PagoRespuesta],
    summary="Listar todos los pagos registrados",
    description="Devuelve el listado completo de pagos persistidos, sin paginación.",
    responses={
        200: {
            "description": "Listado de pagos.",
            "content": {"application/json": {"example": [PAGO_EJEMPLO]}},
        }
    },
)
def get_pagos(bd: Session = Depends(obtener_bd)):
    return listar_pagos(bd)


@router.get(
    "/{id_pago}",
    response_model=PagoRespuesta,
    summary="Obtener un pago por su ID",
    description="Recupera un pago existente a partir de su identificador.",
    responses={
        200: {
            "description": "Pago encontrado.",
            "content": {"application/json": {"example": PAGO_EJEMPLO}},
        },
        404: {
            **NO_ENCONTRADO,
            "description": "No existe un pago con ese ID.",
        },
        422: {
            **VALIDACION,
            "description": "El ID del pago no cumple el formato esperado.",
        },
    },
)
def get_pago(
    id_pago: str = Path(
        ...,
        min_length=1,
        max_length=36,
        description="ID del pago a consultar",
        examples=["9b2c7f41-6e5d-4a3b-9f80-1c2d3e4f5a6b"],
    ),
    bd: Session = Depends(obtener_bd),
):
    return obtener_pago(bd, id_pago)
