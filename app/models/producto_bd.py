from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.base_datos import Base

class ProductoBD(Base):
    __tablename__ = "productos"

    id_producto = Column(String, primary_key=True, index=True)
    nombre_producto = Column(String(50), nullable=False)
    descripcion = Column(String(255), nullable=False)
    stock = Column(Integer, nullable=False)
    stock_minimo = Column(Integer, nullable=False)
    id_categoria = Column(String, ForeignKey("categorias.id_categoria"), nullable=False)
    precio = Column(Integer, nullable=False)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
    
    categoria = relationship("CategoriaBD", back_populates="productos")
