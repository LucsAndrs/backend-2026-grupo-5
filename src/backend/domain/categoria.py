from dataclasses import dataclass, field
from datetime import datetime
import uuid
    
@dataclass
class Categoria:
    nombre_categoria : str
    descripcion : str
    activa : bool 
    fecha_creacion : datetime = field(default_factory=datetime.now)
    fecha_actualizacion : datetime = field(default_factory=datetime.now)
    id_categoria : str = field(default_factory=lambda: str(uuid.uuid4()))