from fastapi import FastAPI, HTTPException
from .domain.categoria import Categoria, CategoriaCreate
from .services.categorias_service import (
    crear_categoria,
    obtener_categoria)

app = FastAPI()

@app.post("/categorias", response_model=Categoria)
def crear_cat(categoria: CategoriaCreate):
    return crear_categoria(categoria)