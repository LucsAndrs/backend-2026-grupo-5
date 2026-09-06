from dataclasses import dataclass, field
from datetime import date
import uuid
    
@dataclass
class Categoria:
    nombre_categoria : str
    descripcion : str
    fecha_creacion : date
    activa : bool
    id_categoria : str = field(default_factory=lambda: str(uuid.uuid4()))