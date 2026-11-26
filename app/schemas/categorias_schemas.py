from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoriaCreate(BaseModel):
    nombre_categoria: str = Field(min_length=1, max_length=50)
    descripcion: str = Field(min_length=1, max_length=255)
    activa: bool

    @field_validator("nombre_categoria", "descripcion")
    @classmethod
    def validar_texto_no_vacio(cls, valor: str) -> str:
        valor_validado = valor.strip()
        if not valor_validado:
            raise ValueError("El valor no puede estar vacío ni contener solo espacios")
        return valor_validado


class CategoriaPatch(BaseModel):
    nombre_categoria: Optional[str] = Field(default=None, min_length=1, max_length=50)
    descripcion: Optional[str] = Field(default=None, min_length=1, max_length=255)
    activa: Optional[bool] = None

    @field_validator("nombre_categoria", "descripcion")
    @classmethod
    def validar_texto_no_vacio(cls, valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return valor
        valor_validado = valor.strip()
        if not valor_validado:
            raise ValueError("El valor no puede estar vacío ni contener solo espacios")
        return valor_validado


class CategoriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_categoria: str
    nombre_categoria: str
    descripcion: str
    activa: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    cantidad_productos: int
