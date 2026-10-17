from fastapi import APIRouter
from app.schemas.pago_schemas import CrearPago, PagoRespuesta
from app.services.pago_service import procesar_pago, obtener_pago, listar_pagos


router = APIRouter(prefix="/pagos", tags=["pagos"])

@router.post("", response_model=PagoRespuesta, status_code=201,
             summary="procesar el pago de una venta")
def post_pago(datos: CrearPago):
    return procesar_pago(datos)

@router.get("", response_model=list[PagoRespuesta],
            summary="listar todos los pagos registrados")
def get_pagos():
    return listar_pagos()

@router.get("/{id_pago}", response_model=PagoRespuesta,
            summary="obtener un pago por su ID")
def get_pago(id_pago: str):
    return obtener_pago(id_pago)