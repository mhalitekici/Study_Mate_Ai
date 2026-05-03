from fastapi import FastAPI
from app.core.database import Base, engine
from app.api.material import router as material_router
from prometheus_fastapi_instrumentator import Instrumentator

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Material Service", version="1.0.0")

Instrumentator().instrument(app).expose(app)

app.include_router(material_router)

@app.get("/")
def root():
    return {"service": "material-service", "status": "running"}