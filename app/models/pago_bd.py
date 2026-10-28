from sqlalchemy import Column, Date, Float, ForeignKey, String
from app.base_datos import Base


class PagoBD(Base):
    __tablename__ = "pagos"

    id_pago = Column(String, primary_key=True, index=True)
    id_venta = Column(
        String,
        ForeignKey("ventas.id_venta"),
        nullable=False,
        index=True,
    )
    fecha_pago = Column(Date, nullable=False)
    monto = Column(Float, nullable=False)
    metodo_pago = Column(String(30), nullable=False)
    estado_pago = Column(String(20), nullable=False)