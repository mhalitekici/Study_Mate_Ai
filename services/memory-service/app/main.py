from fastapi import FastAPI
from app.api.memory import router as memory_router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Memory Service", version="1.0.0")

Instrumentator().instrument(app).expose(app)

app.include_router(memory_router)

@app.get("/")
def root():
    return {"service": "memory-service", "status": "running"}