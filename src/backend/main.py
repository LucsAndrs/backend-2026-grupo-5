from fastapi import FastAPI, HTTPException
from backend.routers.pago_router import router as pago_router

app = FastAPI()

app.include_router(pago_router)