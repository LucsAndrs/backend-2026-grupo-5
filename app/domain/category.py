from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class Category:
    name: str
    description: str
    active: bool
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
