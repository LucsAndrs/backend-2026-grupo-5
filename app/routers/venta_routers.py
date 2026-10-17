from typing import Literal, Optional
from fastapi import APIRouter, Query, status
from app.schemas.venta_schemas import VentaCreada, VentaRespuesta
from app.schemas.common import PaginatedResponse
from app.services.venta_service import venta_servicio


router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("", response_model=VentaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_venta_endpoint(datos: VentaCreada):
    venta = venta_servicio.crear_venta(datos)
    return venta

@router.get("", response_model= PaginatedResponse[VentaRespuesta])
def obtener_ventas(cliente: str = None,
    ordenar_por: Optional[Literal["cliente", "total", "fecha_venta"]] = None,
    direccion: Literal["asc", "desc"] = "asc",
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100)
):
    return venta_servicio.listar_venta(cliente, ordenar_por, direccion, pagina, limite)

@router.get("/{id_venta}", response_model=VentaRespuesta)
def obtener_venta_por_id(id_venta: str):
    return venta_servicio.obtener_venta(id_venta)

@router.get("/{id_venta}/boleta")
def obtener_boleta(id_venta: str):
    return venta_servicio.generar_boleta(id_venta)

@router.delete("/{id_venta}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_venta_endpoint(id_venta: str):
    venta_servicio.eliminar_venta(id_venta)