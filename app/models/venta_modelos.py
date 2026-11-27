from sqlalchemy import Column, String, Float, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from app.base_datos import Base

class VentaBD(Base):
    __tablename__ = "ventas"
    __table_args__ = (
        UniqueConstraint("numero_boleta", name="uq_ventas_numero_boleta"),
    )

    id_venta = Column(String, primary_key=True, index=True)
    cliente = Column(String(90), nullable=False)
    fecha_venta = Column(Date, nullable=False)
    numero_boleta = Column(String(32), nullable=False, index=True)
    total = Column(Float, default=0.0)
    detalles = relationship(
        "DetalleVentaBD",
        back_populates="venta",
        cascade="all, delete-orphan",
        )