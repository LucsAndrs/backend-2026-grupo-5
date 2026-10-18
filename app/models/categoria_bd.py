from sqlalchemy import Column, String, Boolean, DateTime
from app.base_datos import Base


class CategoriaBD(Base):
    __tablename__ = "categorias"

    id_categoria = Column(String, primary_key=True, index=True)
    nombre_categoria = Column(String(50), nullable=False)
    descripcion = Column(String(255), nullable=False)
    activa = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
