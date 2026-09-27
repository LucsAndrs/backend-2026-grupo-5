from dataclasses import dataclass, field
from datetime import datetime 
import uuid

@dataclass
class Producto:
    nombre_producto: str
    descripcion: str
    stock: int
    stock_minimo : int
    id_categoria: str
    precio: int
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    id_producto: str = field(default_factory=lambda: str(uuid.uuid4()))