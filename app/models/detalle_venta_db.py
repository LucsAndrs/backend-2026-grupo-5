from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.base_datos import Base

class DetalleVentaBD(Base):
    __tablename__ = "detalles_ventas"

    id_detalle = Column(String, primary_key=True, index=True)
    id_producto = Column(String, ForeignKey("productos.id_producto"), nullable=False)
    id_venta = Column(String, ForeignKey("ventas.id_venta"), nullable=False)
    cantidad_producto = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    iva = Column(Float, nullable=False, default=0.19)
    descuento = Column(Float, nullable=False, default=0.0)

    # Relación bidireccional con el modelo VentaBD de Elías
    venta = relationship("VentaBD", back_populates="detalles")
