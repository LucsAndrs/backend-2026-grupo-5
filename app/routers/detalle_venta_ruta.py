from fastapi import APIRouter
from typing import List
from app.domain.detalleventa import DetalleVenta
from app.services.detalle_venta_servicio import DetalleVentaServicio

router = APIRouter(prefix="/ventas", tags=["Detalles de Venta"])
service = DetalleVentaServicio()


@router.get("/{id_venta}/detalles", response_model=List[DetalleVenta])
def listar_detalles(id_venta: str):
    return service.obtener_detalles_por_venta(id_venta)

@router.get("/{id_venta}/detalles/{id_detalle}", response_model=DetalleVenta)
def obtener_detalle(id_venta: str, id_detalle: str):
    return service.obtener_detalle_especifico(id_venta, id_detalle)