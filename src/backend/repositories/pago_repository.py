from backend.domain.pago import Pago, EstadoPago

class PagoRepository:
    def __init__(self):
        self._pagos: dict[str, Pago] = {}
    def guardar(self, pago: Pago) -> Pago:
        self._pagos[pago.id_pago] = pago
        return pago
    def obtener_por_id(self, id_pago: str) -> Pago | None:  
        return self._pagos.get(id_pago)
    def listar(self) -> list[Pago]:
        return list(self._pagos.values())
    def obtener_por_venta(self, id_venta: str) -> list[Pago]:
        return [p for p in self._pagos.values() if p.id_venta == id_venta]
    def existe_pago_exitoso(self, id_venta: str) -> bool:
        return any(p.estado_pago == EstadoPago.EXITOSO for p in self.obtener_por_venta(id_venta))
pago_repositorio = PagoRepository()