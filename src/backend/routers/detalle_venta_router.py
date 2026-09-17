from fastapi import APIRouter
from typing import List
from backend.domain.detalleventa import DetalleVenta
from backend.services.detalle_venta_service import DetalleVentaService

router = APIRouter(prefix="/ventas", tags=["Detalles de Venta"])
service = DetalleVentaService()


@router.get("/{id_venta}/detalles", response_model=List[DetalleVenta])
def listar_detalles(id_venta: str):
    return service.obtener_detalles_por_venta(id_venta)

@router.get("/{id_venta}/detalles/{id_detalle}", response_model=DetalleVenta)
def obtener_detalle(id_venta: str, id_detalle: str):
    return service.obtener_detalle_especifico(id_venta, id_detalle)