from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class Product:
    name: str
    description: str
    stock: int
    min_stock: int
    category_id: str
    price: int
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
