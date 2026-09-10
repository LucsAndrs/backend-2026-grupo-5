import uuid
from domain.detalleventa import DetalleVenta
from schemas.detallecreate import DetalleVentaCreate
from repositories.detalle_repository import DetalleVentaRepository

class DetalleVentaService:
    def __init__(self, repositorio: DetalleVentaRepository):
        self.repositorio = repositorio

    def crear_detalle(self, datos: DetalleVentaCreate) -> DetalleVenta:
        precio_unitario = 1500 
        subtotal = precio_unitario * datos.cantidad_producto
        iva = subtotal * 0.19
        descuento = 0.0
        nuevo_detalle = DetalleVenta(
            id_detalle=str(uuid.uuid4()), 
            id_producto=datos.id_producto,
            cantidad_producto=datos.cantidad_producto,
            precio_unitario=precio_unitario,
            subtotal=subtotal,
            iva=iva,
            descuento=descuento
        )

        return self.repositorio.guardar(nuevo_detalle)

    def obtener_detalle(self, id_detalle: str) -> DetalleVenta | None:
        return self.repositorio.obtener_por_id(id_detalle)

    def listar_detalles(self) -> list[DetalleVenta]:
        return self.repositorio.obtener_todos()
        
    def eliminar_detalle(self, id_detalle: str) -> None:
        self.repositorio.eliminar(id_detalle)