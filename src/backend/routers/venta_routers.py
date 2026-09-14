from fastapi import APIRouter, Query, status
from backend.schemas.venta_schemas import VentaCreate, VentaOut
from backend.services.venta_service import(
    crear_venta,
    obtener_venta,
    listar_venta,
    eliminar_venta,
    generar_boleta
)

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("", response_model=VentaOut, status_code=status.HTTP_201_CREATED)
def post_venta(datos: VentaCreate):
    venta = crear_venta(datos)
    return venta

@router.get("")
def get_ventas(cliente: str = None, ordenar_por: str = None, direccion: str = "asc",
               pagina: int = Query(1, ge=1), limite: int = Query(20, ge=1, le=100)):
    return listar_venta(cliente, ordenar_por, direccion, pagina, limite)

@router.get("/{id_venta}", response_model=VentaOut)
def get_venta(id_venta: str):
    return obtener_venta(id_venta)

@router.get("/{id_venta}/boleta")
def get_boleta(id_venta: str):
    venta = obtener_venta(id_venta)
    return generar_boleta(venta)

@router.delete("/{id_venta}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venta(id_venta: str):
    eliminar_venta(id_venta)