from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: ErrorDetail
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Los datos no cumplen las validaciones del esquema",
                    "details": ["body.precio: greater than 0"],
                }
            }
        }
    )


ERROR_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Regla de negocio no cumplida"},
    404: {"model": ErrorResponse, "description": "Recurso no encontrado"},
    409: {"model": ErrorResponse, "description": "Conflicto con el estado actual"},
    422: {"model": ErrorResponse, "description": "Validación de entrada"},
    500: {"model": ErrorResponse, "description": "Error interno del servidor"},
}


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    pagina: int
    limite: int
    total_paginas: int
