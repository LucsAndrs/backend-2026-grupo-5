from dataclasses import dataclass
from datetime import date 

@dataclass
class Producto:
    id_producto: str
    nombre_producto: str
    stock: int
    stock_minimo : int
    precio: int
    fecha_creacion: date
    fecha_actualizacion: date 