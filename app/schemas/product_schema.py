from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class ProductCreate(BaseModel):
    name: str = Field(max_length=50)
    description: str = Field(max_length=255)
    stock: int
    min_stock: int
    category_id: str
    price: int

class ProductPatch(BaseModel):
    name: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)
    stock: Optional[int] = None
    min_stock: Optional[int] = None
    category_id: Optional[str] = None
    price: Optional[int] = None

class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    stock: int
    min_stock: int
    category_id: str
    price: int
    created_at: datetime
    updated_at: datetime
