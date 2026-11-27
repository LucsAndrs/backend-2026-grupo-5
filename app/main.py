from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .excepciones import ApiError
from .routers import categorias_ruta, productos_ruta, venta_ruta
from .routers.pago_ruta import router as pago_router
from .routers.detalle_venta_ruta import router as detalle_venta_router
from .schemas.common import ERROR_RESPONSES, ErrorDetail, ErrorResponse


app = FastAPI(responses=ERROR_RESPONSES)


def _envelope(code: str, message: str, details: list[str]) -> dict:
    return ErrorResponse(error=ErrorDetail(code=code, message=message, details=details)).model_dump()


@app.exception_handler(ApiError)
async def controlar_api_error(request: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope(exc.code, exc.message, exc.details),
    )


@app.exception_handler(RequestValidationError)
async def controlar_validation_error(request: Request, exc: RequestValidationError):
    detalles = [f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()]
    return JSONResponse(
        status_code=422,
        content=_envelope("VALIDATION_ERROR", "Los datos no cumplen las validaciones del esquema", detalles),
    )


@app.exception_handler(StarletteHTTPException)
async def controlar_http_error(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope("HTTP_ERROR", str(exc.detail), []),
    )


@app.exception_handler(IntegrityError)
async def controlar_integrity_error(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content=_envelope("CONFLICT", "El cambio viola una restricción de integridad de la base de datos", []),
    )


@app.exception_handler(Exception)
async def controlar_error_interno(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=_envelope("INTERNAL_ERROR", "Error interno del servidor", []),
    )


app.include_router(venta_ruta.router)
app.include_router(categorias_ruta.router)
app.include_router(productos_ruta.router)
app.include_router(detalle_venta_router)
app.include_router(pago_router)

from .models import categoria_modelos, pago_modelos, producto_modelos, venta_modelos
