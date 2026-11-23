from fastapi import FastAPI
from app.router import router          


app = FastAPI(title="API de Materias", version="1.0.0")
app.include_router(router)               