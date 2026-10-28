from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.base_datos import obtener_bd
from app.schemas.pago_schemas import CrearPago, PagoRespuesta
from app.services.pago_service import (
    listar_pagos,
    obtener_pago,
    procesar_pago,
)


router = APIRouter(prefix="/pagos", tags=["pagos"])


@router.post("", response_model=PagoRespuesta, status_code=201,
             summary="procesar el pago de una venta")
def post_pago(datos: CrearPago, bd: Session = Depends(obtener_bd)):
    return procesar_pago(bd, datos)


@router.get("", response_model=list[PagoRespuesta],
            summary="listar todos los pagos registrados")
def get_pagos(bd: Session = Depends(obtener_bd)):
    return listar_pagos(bd)


@router.get("/{id_pago}", response_model=PagoRespuesta,
            summary="obtener un pago por su ID")
def get_pago(id_pago: str, bd: Session = Depends(obtener_bd)):
    return obtener_pago(bd, id_pago)