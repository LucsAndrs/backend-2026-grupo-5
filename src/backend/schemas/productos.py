from pydantic import BaseModel
from typing import Optional

class ProductoCreate(BaseModel):
    nombre_producto: str
    descripcion: str
    stock: int
    stock_minimo: int
    id_categoria: str
    precio: int
    
class ProductoPatch(BaseModel):
    nombre_producto: Optional[str] = None
    descripcion: Optional[str] = None
    stock: Optional[int] = None
    stock_minimo: Optional[int] = None
    id_categoria: Optional[str] = None
    precio: Optional[int] = None
    