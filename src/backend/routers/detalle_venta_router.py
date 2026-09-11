from fastapi import APIRouter, HTTPException, status
from backend.schemas.detalle_venta_create import DetalleVentaCreate
from backend.services.detalle_venta_service import DetalleVentaService
from backend.repositories.detalle_venta_repository import DetalleVentaRepository

router = APIRouter(prefix="/detalles", tags=["Detalles de Venta"])
repositorio_detalles = DetalleVentaRepository()
servicio_detalles = DetalleVentaService(repositorio_detalles)


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_detalle(datos_entrada: DetalleVentaCreate):
    nuevo_detalle = servicio_detalles.crear_detalle(datos_entrada)
    return nuevo_detalle

@router.get("/", status_code=status.HTTP_200_OK)
def listar_todos_los_detalles():
    return servicio_detalles.listar_detalles()

@router.get("/{id_detalle}", status_code=status.HTTP_200_OK)
def buscar_detalle_por_id(id_detalle: str):
    detalle = servicio_detalles.obtener_detalle(id_detalle)
    if detalle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un detalle con el ID: {id_detalle}"
        )
        
    return detalle

@router.delete("/{id_detalle}", status_code=status.HTTP_200_OK)
def borrar_detalle(id_detalle: str):
    detalle = servicio_detalles.obtener_detalle(id_detalle)
    if detalle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se puede eliminar porque el detalle no existe."
        )       
    servicio_detalles.eliminar_detalle(id_detalle)
    return {"mensaje": "Detalle eliminado correctamente"}