from app.domain.venta import Venta
from app.excepciones import ResourceNotFoundError

class VentaRepositorio:
    def __init__(self):
        self._ventas: list[Venta] = []

    def crear_venta(self, venta: Venta) -> Venta:
        self._ventas.append(venta)
        return venta

    def obtener_por_id(self, id_venta: str) -> Venta:
        for venta in self._ventas:
            if venta.id_venta == id_venta:
                return venta
        raise ResourceNotFoundError(f"No existe una venta con el ID {id_venta}")

    def listar_todas(self) -> list[Venta]:
        return self._ventas

    def eliminar_venta(self, id_venta: str):
        venta = self.obtener_por_id(id_venta)
        self._ventas.remove(venta)

venta_repositorio = VentaRepositorio()