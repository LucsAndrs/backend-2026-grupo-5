from backend.domain.venta import Venta

class VentaRepository:
    def __init__(self):
        self.diccionario = {}
        self.nuevo_id = 1

    def crear_venta(self, venta: Venta):
        venta.id = self.nuevo_id
        self.diccionario[venta.id] = venta
        self.nuevo_id = self.nuevo_id + 1
        return venta

    def obtener_por_id(self, id_venta: int):
        return self.diccionario.get(id_venta)

    def listar_todas(self):
        return list(self.diccionario.values())

venta_repositorio = VentaRepository()
