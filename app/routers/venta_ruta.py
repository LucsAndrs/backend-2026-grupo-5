from typing import Literal, Optional
from fastapi import APIRouter, Query, status, Depends
from sqlalchemy.orm import Session

from app.schemas.venta_esquemas import BoletaResponse, VentaCreada, VentaRespuesta
from app.schemas.common import PaginatedResponse
from app.services.venta_servicio import venta_servicio
from app.base_datos import obtener_bd

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("", response_model=VentaRespuesta, status_code=status.HTTP_201_CREATED,
             summary="Crear venta", description="Registra la venta, descuenta el stock y genera un numero_boleta único.")
def crear_venta_endpoint(datos: VentaCreada, bd: Session = Depends(obtener_bd)):
    venta = venta_servicio.crear_venta(bd, datos)
    return venta

@router.get("", response_model=PaginatedResponse[VentaRespuesta],
            summary="Listar ventas", description="Devuelve ventas paginadas con filtro por cliente y orden.")
def obtener_ventas(cliente: str = None,
    ordenar_por: Optional[Literal["cliente", "total", "fecha_venta"]] = None,
    direccion: Literal["asc", "desc"] = "asc",
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    bd: Session = Depends(obtener_bd)
):
    return venta_servicio.listar_venta(bd, cliente, ordenar_por, direccion, pagina, limite)

@router.get("/{id_venta}", response_model=VentaRespuesta,
            summary="Obtener venta", description="Recupera una venta por su ID, incluyendo numero_boleta.")
def obtener_venta_por_id(id_venta: str, bd: Session = Depends(obtener_bd)):
    return venta_servicio.obtener_venta(bd, id_venta)

@router.get("/{id_venta}/boleta", response_model=BoletaResponse,
            summary="Obtener boleta", description="Devuelve los ítems, total y numero_boleta de la venta.")
def obtener_boleta(id_venta: str, bd: Session = Depends(obtener_bd)):
    return venta_servicio.generar_boleta(bd, id_venta)

@router.delete("/{id_venta}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar venta", description="Elimina la venta y devuelve el stock al eliminar detalles.")
def eliminar_venta_endpoint(id_venta: str, bd: Session = Depends(obtener_bd)):
    venta_servicio.eliminar_venta(bd, id_venta)