from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class CategoryCreate(BaseModel):
    name: str = Field(max_length=50)
    description: str = Field(max_length=255)
    active: bool

class CategoryPatch(BaseModel):
    name: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)
    active: Optional[bool] = None

class CategoryResponse(BaseModel):
    id: str
    name: str
    description: str
    active: bool
    created_at: datetime
    updated_at: datetime
    product_count: int
