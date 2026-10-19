from typing import Literal, Optional
from fastapi import APIRouter, Query, status, Depends
from sqlalchemy.orm import Session

from app.schemas.venta_esquemas import VentaCreada, VentaRespuesta
from app.schemas.common import PaginatedResponse
from app.services.venta_servicio import venta_servicio
from app.base_datos import obtener_bd

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("", response_model=VentaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_venta_endpoint(datos: VentaCreada, bd: Session = Depends(obtener_bd)):
    venta = venta_servicio.crear_venta(bd, datos)
    return venta

@router.get("", response_model= PaginatedResponse[VentaRespuesta])
def obtener_ventas(cliente: str = None,
    ordenar_por: Optional[Literal["cliente", "total", "fecha_venta"]] = None,
    direccion: Literal["asc", "desc"] = "asc",
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    bd: Session = Depends(obtener_bd)
):
    return venta_servicio.listar_venta(bd, cliente, ordenar_por, direccion, pagina, limite)

@router.get("/{id_venta}", response_model=VentaRespuesta)
def obtener_venta_por_id(id_venta: str, bd: Session = Depends(obtener_bd)):
    return venta_servicio.obtener_venta(bd, id_venta)

@router.get("/{id_venta}/boleta")
def obtener_boleta(id_venta: str, bd: Session = Depends(obtener_bd)):
    return venta_servicio.generar_boleta(bd, id_venta)

@router.delete("/{id_venta}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_venta_endpoint(id_venta: str, bd: Session = Depends(obtener_bd)):
    venta_servicio.eliminar_venta(bd, id_venta)