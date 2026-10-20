from fastapi import APIRouter, Depends
from typing import List
from app.domain.detalleventa import DetalleVenta
from app.services.detalle_venta_servicio import DetalleVentaServicio
from sqlalchemy.orm import Session
from app.base_datos import obtener_bd

router = APIRouter(prefix="/ventas", tags=["Detalles de Venta"])
service = DetalleVentaServicio()


@router.get("/{id_venta}/detalles", response_model=List[DetalleVenta])
def listar_detalles(
    id_venta: str,
    bd: Session = Depends(obtener_bd),                
):
    return service.obtener_detalles_por_venta(bd, id_venta)

@router.get("/{id_venta}/detalles/{id_detalle}", response_model=DetalleVenta)
def obtener_detalle(
    id_venta: str, 
    id_detalle: str,
    bd: Session = Depends(obtener_bd),
):
    return service.obtener_detalle_especifico(bd, id_venta, id_detalle)
