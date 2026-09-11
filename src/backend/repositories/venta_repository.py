from backend.domain.venta import Venta

ventas: list[Venta] = []

def crear_venta(venta: Venta):
    ventas.append(venta)
    return venta

def obtener_por_id(id_venta: str):
    for venta in ventas:
        if venta.id_venta == id_venta:
            return venta
    raise KeyError("Venta no encontrada")

def listar_todas():
    return ventas
