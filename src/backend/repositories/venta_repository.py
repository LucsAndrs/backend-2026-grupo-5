from backend.domain.venta import Venta
from backend.domain.excepciones import RecursoNoEncontradoError

ventas: list[Venta] = []

def crear_venta(venta: Venta):
    ventas.append(venta)
    return venta

def obtener_por_id(id_venta: str):
    for venta in ventas:
        if venta.id_venta == id_venta:
            return venta
    raise RecursoNoEncontradoError(f"No existe una venta con el ID {id_venta}")

def listar_todas():
    return ventas

def eliminar_venta(id_venta: str):
    venta = obtener_por_id(id_venta)
    ventas.remove(venta)