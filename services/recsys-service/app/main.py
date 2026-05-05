from fastapi import FastAPI
from app.api.recsys import router as recsys_router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="RecSys Service", version="1.0.0")

Instrumentator().instrument(app).expose(app)

app.include_router(recsys_router)

@app.get("/")
def root():
    return {"service": "recsys-service", "status": "running"}