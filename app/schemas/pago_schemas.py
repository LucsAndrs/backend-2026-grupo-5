from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.pago import EstadoPago, MetodoPago


class CrearPago(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id_venta": "d3f1c2a4-5b6e-4f7a-8c9d-0e1f2a3b4c5d",
                "monto": 2400,
                "metodo_pago": "debito",
            }
        }
    )

    id_venta: str = Field(
        min_length=1,
        max_length=36,
        strip_whitespace=True,
        description="ID de la venta que se va a pagar",
    )
    monto: float = Field(
        gt=0,
        allow_inf_nan=False,
        description="Monto del pago; debe coincidir con el total de la venta y tener máximo dos decimales",
    )
    metodo_pago: MetodoPago = Field(description="Método de pago: 'debito' o 'credito'")

    @field_validator("id_venta", mode="before")
    @classmethod
    def normalizar_id_venta(cls, valor: object) -> object:
        if isinstance(valor, str):
            return valor.strip()
        return valor

    @field_validator("monto")
    @classmethod
    def validar_precision_monto(cls, valor: float) -> float:
        if Decimal(str(valor)) != Decimal(str(valor)).quantize(Decimal("0.01")):
            raise ValueError("El monto debe tener como máximo dos decimales")
        return valor

    @field_validator("metodo_pago", mode="before")
    @classmethod
    def normalizar_metodo_pago(cls, valor: object) -> object:
        if isinstance(valor, str):
            return valor.strip().lower()
        return valor


class PagoRespuesta(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id_pago": "9b2c7f41-6e5d-4a3b-9f80-1c2d3e4f5a6b",
                "id_venta": "d3f1c2a4-5b6e-4f7a-8c9d-0e1f2a3b4c5d",
                "fecha_pago": "2026-11-25",
                "monto": 2400,
                "metodo_pago": "debito",
                "estado_pago": "exitoso",
            }
        },
    )

    id_pago: str = Field(description="ID del pago")
    id_venta: str = Field(description="ID de la venta pagada")
    fecha_pago: date = Field(description="Fecha en que se registró el pago")
    monto: float = Field(ge=0, description="Monto pagado")
    metodo_pago: MetodoPago = Field(description="Método de pago utilizado")
    estado_pago: EstadoPago = Field(description="Estado del pago")
