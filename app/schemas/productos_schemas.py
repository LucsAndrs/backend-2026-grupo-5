from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductoCreate(BaseModel):
    nombre_producto: str = Field(min_length=1, max_length=50)
    descripcion: str = Field(min_length=1, max_length=255)
    stock: int = Field(ge=0)
    stock_minimo: int = Field(ge=0)
    id_categoria: str = Field(min_length=1)
    precio: int = Field(ge=0)

    @field_validator("nombre_producto", "descripcion", "id_categoria")
    @classmethod
    def validar_texto_no_vacio(cls, valor: str) -> str:
        valor_validado = valor.strip()
        if not valor_validado:
            raise ValueError("El valor no puede estar vacío ni contener solo espacios")
        return valor_validado


class ProductoPatch(BaseModel):
    nombre_producto: Optional[str] = Field(default=None, min_length=1, max_length=50)
    descripcion: Optional[str] = Field(default=None, min_length=1, max_length=255)
    stock: Optional[int] = Field(default=None, ge=0)
    stock_minimo: Optional[int] = Field(default=None, ge=0)
    id_categoria: Optional[str] = Field(default=None, min_length=1)
    precio: Optional[int] = Field(default=None, ge=0)

    @field_validator("nombre_producto", "descripcion", "id_categoria")
    @classmethod
    def validar_texto_no_vacio(cls, valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return valor
        valor_validado = valor.strip()
        if not valor_validado:
            raise ValueError("El valor no puede estar vacío ni contener solo espacios")
        return valor_validado


class ProductoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_producto: str
    nombre_producto: str
    descripcion: str
    stock: int
    stock_minimo: int
    id_categoria: str
    precio: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
