from fastapi import FastAPI
from .routers import categoria

app = FastAPI()

app.include_router(categoria.router)
