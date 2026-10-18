import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

URL_BASE_DATOS = os.getenv("DATABASE_URL", "sqlite:///./minimarket.db")

if URL_BASE_DATOS.startswith("sqlite"):
    motor = create_engine(URL_BASE_DATOS, connect_args={"check_same_thread": False})
else:
    motor = create_engine(URL_BASE_DATOS)


SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)

Base = declarative_base()

def obtener_bd():
    bd = SesionLocal()
    try:
        yield bd
    finally:
        bd.close()