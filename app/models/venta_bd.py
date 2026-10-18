from sqlalchemy import Column, String, Float, Date
from sqlalchemy.orm import relationship
from app.base_datos import Base

class VentaBD(Base):
    __tablename__ = "ventas"
    
    id_venta = Column(String, primary_key=True, index=True)
    cliente = Column(String, nullable=False)
    fecha_venta = Column(Date, nullable=False)
    total = Column(Float=0.0)


    detalles = relationship("DetalleVentaBD", back_populates="venta", cascade="all, delete-orphan")