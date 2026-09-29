from typing import Literal, Optional
from fastapi import APIRouter, Query, status
from backend.schemas.venta_schemas import VentaCreate, VentaOut
from backend.schemas.common import PaginatedResponse
from backend.services.venta_service import(
    crear_venta,
    obtener_venta,
    listar_venta,
    eliminar_venta,
    generar_boleta
)

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("", response_model=VentaOut, status_code=status.HTTP_201_CREATED)
def crear_venta_endpoint(datos: VentaCreate):
    venta = crear_venta(datos)
    return venta

@router.get("", response_model= PaginatedResponse[VentaOut])
def obtener_ventas(cliente: str = None,
               ordenar_por: Optional[Literal["cliente", "total", "fecha_venta"]] = None,
               direccion: Literal["asc", "desc"] = "asc",
               pagina: int = Query(1, ge=1),
               limite: int = Query(20, ge=1, le=100)
):
    return listar_venta(cliente, ordenar_por, direccion, pagina, limite)

@router.get("/{id_venta}", response_model=VentaOut)
def obtener_venta_por_id(id_venta: str):
    return obtener_venta(id_venta)

@router.get("/{id_venta}/boleta")
def obtener_boleta(id_venta: str):
    venta = obtener_venta(id_venta)
    return generar_boleta(venta)

@router.delete("/{id_venta}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_venta_endpoint(id_venta: str):
    eliminar_venta(id_venta)