from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.base_datos import obtener_bd
from app.schemas.common import ErrorResponse
from app.schemas.detalle_venta_esquema import DetalleVentaConsulta
from app.services.detalle_venta_servicio import DetalleVentaServicio

router = APIRouter(prefix="/ventas", tags=["Detalles de Venta"])
service = DetalleVentaServicio()

EJEMPLO_DETALLE = {
    "id_detalle": "demo-detalle-001",
    "id_venta": "demo-venta-001",
    "id_producto": "demo-arroz",
    "cantidad_producto": 2,
    "precio_unitario": 1200,
    "subtotal": 2400,
    "iva": 0.0,
    "descuento": 0.0,
}


@router.get(
    "/{id_venta}/detalles",
    response_model=list[DetalleVentaConsulta],
    summary="Listar los detalles de una venta",
    description="Devuelve los detalles de la venta. Si no hay coincidencias, devuelve una lista vacía.",
    responses={
        200: {
            "description": "Lista de detalles de la venta.",
            "content": {"application/json": {"example": [EJEMPLO_DETALLE]}},
        },
    },
)
def listar_detalles(
    id_venta: Annotated[str, Path(description="ID de la venta", examples=["demo-venta-001"])],
    bd: Session = Depends(obtener_bd),
) -> list[DetalleVentaConsulta]:
    detalles = service.obtener_detalles_por_venta(bd, id_venta)
    return [DetalleVentaConsulta.model_validate(detalle) for detalle in detalles]


@router.get(
    "/{id_venta}/detalles/{id_detalle}",
    response_model=DetalleVentaConsulta,
    summary="Obtener un detalle de una venta",
    description="Busca un detalle por su ID dentro de la venta indicada.",
    responses={
        200: {
            "description": "Detalle encontrado.",
            "content": {"application/json": {"example": EJEMPLO_DETALLE}},
        },
        404: {
            "model": ErrorResponse,
            "description": "El detalle no existe dentro de la venta indicada.",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "RESOURCE_NOT_FOUND",
                            "message": "El detalle demo-detalle-999 no existe en la venta demo-venta-001",
                            "details": [],
                        }
                    }
                }
            },
        },
    },
)
def obtener_detalle(
    id_venta: Annotated[str, Path(description="ID de la venta", examples=["demo-venta-001"])],
    id_detalle: Annotated[str, Path(description="ID del detalle", examples=["demo-detalle-001"])],
    bd: Session = Depends(obtener_bd),
) -> DetalleVentaConsulta:
    detalle = service.obtener_detalle_especifico(bd, id_venta, id_detalle)
    return DetalleVentaConsulta.model_validate(detalle)