from fastapi import FastAPI, HTTPException
from routers import detalle_venta_router

app = FastAPI()
app.include_router(detalle_venta_router.router)