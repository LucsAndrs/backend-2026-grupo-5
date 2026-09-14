from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.exceptions import ApiError
from .routers import categoria
from .schemas.common import ErrorDetail, ErrorResponse

app = FastAPI()


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


app.include_router(categoria.router)
